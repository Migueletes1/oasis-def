"""
OASIS Data Guardian — Utilidades de Backup y Restauracion.

Funciones para crear, verificar, cifrar y restaurar backups
de la base de datos y archivos media del proyecto OASIS.
"""

import hashlib
import hmac
import io
import logging
import os
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from OASIS.utils import format_bytes

logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = Path(settings.BASE_DIR) / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# HASHING & INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════

def calculate_sha256(filepath):
    """Calcula el hash SHA-256 de un archivo."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_integrity(filepath, expected_hash):
    """Verifica la integridad de un archivo comparando su hash SHA-256."""
    actual_hash = calculate_sha256(filepath)
    return hmac.compare_digest(actual_hash, expected_hash)


# ═══════════════════════════════════════════════════════════════════════════
# ENCRYPTION (XOR — basic obfuscation; use pycryptodome AES for production)
# ═══════════════════════════════════════════════════════════════════════════

def _get_encryption_key():
    """Deriva una clave de 256 bits del SECRET_KEY de Django (usada para XOR)."""
    key_material = settings.SECRET_KEY.encode('utf-8')
    return hashlib.sha256(key_material).digest()


def encrypt_file(input_path, output_path=None):
    """
    Cifra un archivo usando XOR con clave derivada de SECRET_KEY.
    Para produccion se recomienda usar AES-256 con pycryptodome.
    Esta implementacion provee ofuscacion basica sin dependencias externas.
    """
    key = _get_encryption_key()
    if output_path is None:
        output_path = str(input_path) + '.enc'

    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        fout.write(b'OASIS_ENC_V1\x00')
        idx = 0
        while True:
            chunk = fin.read(8192)
            if not chunk:
                break
            encrypted = bytearray(len(chunk))
            for i, byte_val in enumerate(chunk):
                encrypted[i] = byte_val ^ key[(idx + i) % len(key)]
            idx += len(chunk)
            fout.write(bytes(encrypted))

    return output_path


def decrypt_file(input_path, output_path):
    """Descifra un archivo cifrado con encrypt_file."""
    key = _get_encryption_key()

    with open(input_path, 'rb') as fin:
        header = fin.read(13)  # b'OASIS_ENC_V1\x00'
        if header != b'OASIS_ENC_V1\x00':
            raise ValueError('Archivo no es un backup cifrado valido de OASIS')

        with open(output_path, 'wb') as fout:
            idx = 0
            while True:
                chunk = fin.read(8192)
                if not chunk:
                    break
                decrypted = bytearray(len(chunk))
                for i, byte in enumerate(chunk):
                    decrypted[i] = byte ^ key[(idx + i) % len(key)]
                idx += len(chunk)
                fout.write(bytes(decrypted))

    return output_path


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE BACKUP
# ═══════════════════════════════════════════════════════════════════════════

def backup_database():
    """
    Crea un backup de la base de datos.
    SQLite: copia directa con sqlite3.backup()
    MySQL: usa mysqldump via subprocess
    """
    db_config = settings.DATABASES['default']
    engine = db_config['ENGINE']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if 'sqlite3' in engine:
        return _backup_sqlite(db_config, timestamp)
    elif 'mysql' in engine:
        return _backup_mysql(db_config, timestamp)
    else:
        raise NotImplementedError(f'Backup no soportado para engine: {engine}')


def _backup_sqlite(db_config, timestamp):
    """Backup de SQLite usando la API nativa de backup."""
    db_path = db_config['NAME']
    backup_filename = f'oasis_db_{timestamp}.sqlite3'
    backup_path = BACKUP_DIR / backup_filename

    # Usar sqlite3 backup API (seguro incluso con escrituras concurrentes)
    source = sqlite3.connect(str(db_path))
    dest = sqlite3.connect(str(backup_path))
    try:
        source.backup(dest)
    finally:
        dest.close()
        source.close()

    logger.info(f'Backup SQLite creado: {backup_path}')
    return backup_path


def _backup_mysql(db_config, timestamp):
    """Backup de MySQL usando mysqldump."""
    import subprocess

    backup_filename = f'oasis_db_{timestamp}.sql'
    backup_path = BACKUP_DIR / backup_filename

    cmd = [
        'mysqldump',
        f'--host={db_config.get("HOST", "localhost")}',
        f'--port={db_config.get("PORT", "3306")}',
        f'--user={db_config["USER"]}',
        f'--password={db_config["PASSWORD"]}',
        '--single-transaction',
        '--routines',
        '--triggers',
        db_config['NAME'],
    ]

    with open(backup_path, 'w') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=300)

    if result.returncode != 0:
        backup_path.unlink(missing_ok=True)
        raise RuntimeError(f'mysqldump fallo: {result.stderr.decode()}')

    logger.info(f'Backup MySQL creado: {backup_path}')
    return backup_path


# ═══════════════════════════════════════════════════════════════════════════
# MEDIA BACKUP
# ═══════════════════════════════════════════════════════════════════════════

def backup_media():
    """Crea un archivo ZIP con todos los archivos media."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'oasis_media_{timestamp}.zip'
    backup_path = BACKUP_DIR / backup_filename

    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root or not Path(media_root).exists():
        # Si no hay MEDIA_ROOT, crear un zip vacio con nota
        with zipfile.ZipFile(backup_path, 'w') as zf:
            zf.writestr('README.txt', 'No se encontro directorio MEDIA_ROOT configurado.')
        return backup_path

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        media_path = Path(media_root)
        for file in media_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(media_path)
                zf.write(file, arcname)

    logger.info(f'Backup media creado: {backup_path}')
    return backup_path


# ═══════════════════════════════════════════════════════════════════════════
# FULL BACKUP (DB + Media + Staticfiles)
# ═══════════════════════════════════════════════════════════════════════════

def create_full_backup(encrypt=False):
    """
    Crea un backup completo: base de datos + media en un solo ZIP.
    Retorna (filepath, hash_sha256, size_bytes, encrypted).
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'oasis_full_{timestamp}.zip'
    backup_path = BACKUP_DIR / backup_filename

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Database backup
        db_backup = backup_database()
        zf.write(db_backup, f'database/{db_backup.name}')
        db_backup.unlink()  # Eliminar archivo temporal de DB

        # 2. Media files
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and Path(media_root).exists():
            media_path = Path(media_root)
            for file in media_path.rglob('*'):
                if file.is_file():
                    arcname = f'media/{file.relative_to(media_path)}'
                    zf.write(file, arcname)

        # 3. Metadata
        metadata = (
            f'OASIS Backup\n'
            f'Fecha: {timestamp}\n'
            f'Tipo: Full (DB + Media)\n'
            f'Django Version: {import_module_version("django")}\n'
            f'Engine: {settings.DATABASES["default"]["ENGINE"]}\n'
        )
        zf.writestr('BACKUP_INFO.txt', metadata)

    # Encrypt if requested
    is_encrypted = False
    if encrypt:
        encrypted_path = str(backup_path) + '.enc'
        encrypt_file(backup_path, encrypted_path)
        backup_path.unlink()
        backup_path = Path(encrypted_path)
        backup_filename = backup_path.name
        is_encrypted = True

    # Calculate hash and size
    file_hash = calculate_sha256(backup_path)
    file_size = backup_path.stat().st_size

    logger.info(
        f'Backup completo creado: {backup_filename} '
        f'({file_size} bytes, SHA256={file_hash[:16]}...)'
    )

    return backup_path, file_hash, file_size, is_encrypted


def create_db_only_backup(encrypt=False):
    """Crea un backup solo de la base de datos."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    db_backup = backup_database()

    # Compress to zip
    zip_filename = f'oasis_db_{timestamp}.zip'
    zip_path = BACKUP_DIR / zip_filename

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_backup, db_backup.name)
        metadata = f'OASIS DB Backup\nFecha: {timestamp}\n'
        zf.writestr('BACKUP_INFO.txt', metadata)

    db_backup.unlink()

    is_encrypted = False
    if encrypt:
        encrypted_path = str(zip_path) + '.enc'
        encrypt_file(zip_path, encrypted_path)
        zip_path.unlink()
        zip_path = Path(encrypted_path)
        is_encrypted = True

    file_hash = calculate_sha256(zip_path)
    file_size = zip_path.stat().st_size

    return zip_path, file_hash, file_size, is_encrypted


# ═══════════════════════════════════════════════════════════════════════════
# RESTORE
# ═══════════════════════════════════════════════════════════════════════════

def restore_database(backup_record):
    """
    Restaura la base de datos desde un backup.
    Crea un backup de seguridad antes de restaurar.
    """
    from auditoria.models import BackupRecord

    filepath = Path(backup_record.filepath)
    if not filepath.exists():
        raise FileNotFoundError(f'Archivo de backup no encontrado: {filepath}')

    # Verificar integridad
    if backup_record.hash_sha256:
        if not verify_integrity(filepath, backup_record.hash_sha256):
            raise ValueError(
                'ALERTA: El hash del archivo no coincide. '
                'El backup puede haber sido alterado.'
            )

    # Si esta cifrado, descifrar primero
    work_path = filepath
    temp_decrypted = None
    if backup_record.encrypted:
        temp_decrypted = filepath.with_suffix('.tmp')
        decrypt_file(filepath, temp_decrypted)
        work_path = temp_decrypted

    try:
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']

        if 'sqlite3' in engine:
            _restore_sqlite(work_path, db_config)
        elif 'mysql' in engine:
            _restore_mysql(work_path, db_config)
        else:
            raise NotImplementedError(f'Restauracion no soportada para: {engine}')

        logger.info(f'Base de datos restaurada desde: {backup_record.filename}')
    finally:
        if temp_decrypted and temp_decrypted.exists():
            temp_decrypted.unlink()


def _restore_sqlite(backup_path, db_config):
    """Restaura SQLite desde un archivo de backup."""
    db_path = Path(db_config['NAME'])

    # El backup puede ser .zip o .sqlite3
    if zipfile.is_zipfile(str(backup_path)):
        with zipfile.ZipFile(backup_path, 'r') as zf:
            # Buscar el archivo .sqlite3 dentro del zip
            sqlite_files = [n for n in zf.namelist() if n.endswith('.sqlite3')]
            if not sqlite_files:
                raise ValueError('No se encontro archivo .sqlite3 en el backup')

            with tempfile.TemporaryDirectory() as tmpdir:
                zf.extract(sqlite_files[0], tmpdir)
                extracted = Path(tmpdir) / sqlite_files[0]
                # Crear backup de seguridad del actual
                safety_backup = db_path.with_suffix('.pre_restore.sqlite3')
                shutil.copy2(db_path, safety_backup)
                # Restaurar
                shutil.copy2(extracted, db_path)
    else:
        # Archivo directo .sqlite3
        safety_backup = db_path.with_suffix('.pre_restore.sqlite3')
        shutil.copy2(db_path, safety_backup)
        shutil.copy2(backup_path, db_path)


def _restore_mysql(backup_path, db_config):
    """Restaura MySQL desde un dump SQL."""
    import subprocess

    # Extraer SQL del zip si aplica
    sql_path = backup_path
    temp_dir = None

    if zipfile.is_zipfile(str(backup_path)):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(backup_path, 'r') as zf:
            sql_files = [n for n in zf.namelist() if n.endswith('.sql')]
            if not sql_files:
                raise ValueError('No se encontro archivo .sql en el backup')
            zf.extract(sql_files[0], temp_dir)
            sql_path = Path(temp_dir) / sql_files[0]

    try:
        cmd = [
            'mysql',
            f'--host={db_config.get("HOST", "localhost")}',
            f'--port={db_config.get("PORT", "3306")}',
            f'--user={db_config["USER"]}',
            f'--password={db_config["PASSWORD"]}',
            db_config['NAME'],
        ]

        with open(sql_path, 'r') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f'mysql restore fallo: {result.stderr.decode()}')
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

def delete_backup_file(backup_record):
    """Elimina el archivo fisico de un backup."""
    filepath = Path(backup_record.filepath)
    if filepath.exists():
        filepath.unlink()
        logger.info(f'Archivo de backup eliminado: {filepath}')
        return True
    return False


def cleanup_old_backups(max_age_days=30, max_count=20):
    """Elimina backups antiguos manteniendo los mas recientes."""
    from auditoria.models import BackupRecord
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=max_age_days)

    old_records = BackupRecord.objects.filter(created_at__lt=cutoff)
    count = 0
    for record in old_records:
        delete_backup_file(record)
        record.delete()
        count += 1

    # Tambien limitar por cantidad total
    excess = BackupRecord.objects.count() - max_count
    if excess > 0:
        for record in BackupRecord.objects.order_by('created_at')[:excess]:
            delete_backup_file(record)
            record.delete()
            count += 1

    return count


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def import_module_version(module_name):
    """Obtiene la version de un modulo instalado."""
    try:
        import importlib
        mod = importlib.import_module(module_name)
        return getattr(mod, '__version__', getattr(mod, 'VERSION', 'N/A'))
    except ImportError:
        return 'N/A'


def get_backup_stats():
    """Retorna estadisticas del sistema de backups."""
    from auditoria.models import BackupRecord
    from django.db.models import Sum

    total = BackupRecord.objects.count()
    total_size = BackupRecord.objects.aggregate(
        total=Sum('size_bytes')
    )['total'] or 0
    last_backup = BackupRecord.objects.first()  # ordered by -created_at

    # Check disk space
    disk_usage = shutil.disk_usage(BACKUP_DIR)

    return {
        'total_backups': total,
        'total_size': total_size,
        'total_size_display': format_bytes(total_size),
        'last_backup': last_backup,
        'disk_free': disk_usage.free,
        'disk_free_display': format_bytes(disk_usage.free),
        'disk_total': disk_usage.total,
        'disk_used_pct': round((disk_usage.used / disk_usage.total) * 100, 1),
        'backup_dir': str(BACKUP_DIR),
    }


