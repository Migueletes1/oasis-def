from django.db import models

from OASIS.utils import format_bytes


class Auditoria(models.Model):
    accion = models.CharField(max_length=50)
    tabla = models.CharField(max_length=50)
    registro_id = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.accion} en {self.tabla} ({self.fecha})"


class BackupRecord(models.Model):
    """Registro de backups del sistema OASIS."""

    class TipoBackup(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        AUTO = 'auto', 'Automatico'

    class TipoContenido(models.TextChoices):
        DATABASE = 'database', 'Base de Datos'
        MEDIA = 'media', 'Archivos Media'
        FULL = 'full', 'Completo'

    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500)
    size_bytes = models.BigIntegerField(default=0)
    tipo = models.CharField(
        max_length=10,
        choices=TipoBackup.choices,
        default=TipoBackup.MANUAL,
    )
    contenido = models.CharField(
        max_length=10,
        choices=TipoContenido.choices,
        default=TipoContenido.FULL,
    )
    hash_sha256 = models.CharField(max_length=64, blank=True)
    encrypted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'

    def __str__(self):
        return f"{self.filename} ({self.get_tipo_display()} - {self.created_at:%d/%m/%Y %H:%M})"

    @property
    def size_display(self):
        return format_bytes(self.size_bytes)
