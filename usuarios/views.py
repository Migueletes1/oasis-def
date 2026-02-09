import json
import logging
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from OASIS.utils import get_client_ip
from .forms import LoginForm, EmpresaRegistroForm
from .models import Usuario

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """Decorator: requires authenticated admin/superuser. Returns 403 JSON otherwise."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not (request.user.es_admin or request.user.is_superuser):
            return JsonResponse({'error': 'Acceso denegado'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped


# ═══════════════════════════════════════════════════════════════════════════
# AUTH VIEWS
# ═══════════════════════════════════════════════════════════════════════════

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de inicio de sesion con proteccion CSRF."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Login exitoso: {user.username} (rol={user.rol})")
            messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}.')
            next_url = request.GET.get('next', '')
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = 'index'
            return redirect(next_url)
        else:
            logger.warning(f"Intento de login fallido desde IP: {get_client_ip(request)}")
            messages.error(request, 'Credenciales invalidas. Verifica tu usuario y contrasena.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def registro_empresa_view(request):
    """
    Registro exclusivo para empresas.
    La cuenta se crea con is_active=False hasta aprobacion del admin.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = EmpresaRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(
                f"Solicitud de registro empresa: {user.nombre_empresa} "
                f"NIT={user.nit_empresa} email={user.email}"
            )
            messages.success(
                request,
                'Tu solicitud de registro ha sido enviada exitosamente. '
                'Un administrador revisara tu cuenta y recibiras un correo '
                'cuando sea aprobada.'
            )
            return redirect('registro_pendiente')
    else:
        form = EmpresaRegistroForm()

    return render(request, 'usuarios/registro_empresa.html', {'form': form})


def registro_pendiente_view(request):
    """Pagina de confirmacion post-registro."""
    return render(request, 'usuarios/registro_pendiente.html')


@login_required
def logout_view(request):
    """Cierre de sesion seguro (POST only para prevenir CSRF logout)."""
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        logger.info(f"Logout: {username}")
        messages.info(request, 'Has cerrado sesion correctamente.')
    return redirect('index')


@login_required
def perfil_view(request):
    """Vista de perfil del usuario autenticado."""
    return render(request, 'usuarios/perfil.html')


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD VIEWS
# ═══════════════════════════════════════════════════════════════════════════

@login_required
def dashboard_view(request):
    """Dashboard segun rol del usuario."""
    user = request.user

    if user.is_superuser or user.es_admin:
        context = _build_admin_context(user)
        return render(request, 'usuarios/dashboard_admin.html', context)

    template_map = {
        'empresa': 'usuarios/dashboard_empresa.html',
        'instructor': 'usuarios/dashboard_instructor.html',
        'aprendiz': 'usuarios/dashboard_aprendiz.html',
    }
    template = template_map.get(user.rol, 'usuarios/dashboard_aprendiz.html')
    return render(request, template, {'usuario': user})


def _build_admin_context(user):
    """Construye todo el contexto para el dashboard de administrador."""
    from datetime import timedelta
    from repositorio.models import (
        ProyectoGrado, CLUSTER_CHOICES, CARRERA_CHOICES, CARRERA_A_CLUSTER,
    )
    from auditoria.models import Auditoria
    from aprendices.models import Aprendiz
    from instructores.models import Instructor
    from proyectos.models import Proyecto

    now = timezone.now()

    # ─── KPIs ───────────────────────────────────────────────────────────
    total_proyectos_grado = ProyectoGrado.objects.count()
    total_proyectos = Proyecto.objects.count()
    empresas_activas = Usuario.objects.filter(rol='empresa', is_active=True).count()
    total_aprendices = Aprendiz.objects.count()
    total_instructores = Instructor.objects.count()
    total_usuarios = Usuario.objects.count()

    # ─── Growth % (mes actual vs mes anterior) ───────────────────────
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = this_month_start - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    proyectos_this_month = ProyectoGrado.objects.filter(
        fecha_publicacion__gte=this_month_start
    ).count()
    proyectos_last_month = ProyectoGrado.objects.filter(
        fecha_publicacion__gte=last_month_start,
        fecha_publicacion__lt=this_month_start,
    ).count()
    growth_proyectos = _calc_growth(proyectos_this_month, proyectos_last_month)

    empresas_this_month = Usuario.objects.filter(
        rol='empresa', is_active=True, date_joined__gte=this_month_start,
    ).count()
    empresas_last_month = Usuario.objects.filter(
        rol='empresa', is_active=True,
        date_joined__gte=last_month_start, date_joined__lt=this_month_start,
    ).count()
    growth_empresas = _calc_growth(empresas_this_month, empresas_last_month)

    usuarios_this_month = Usuario.objects.filter(date_joined__gte=this_month_start).count()
    usuarios_last_month = Usuario.objects.filter(
        date_joined__gte=last_month_start, date_joined__lt=this_month_start,
    ).count()
    growth_usuarios = _calc_growth(usuarios_this_month, usuarios_last_month)

    # ─── Carrera lider (mas proyectos) ───────────────────────────────
    top_carrera_qs = (
        ProyectoGrado.objects.values('carrera')
        .annotate(c=Count('id'))
        .order_by('-c')
        .first()
    )
    carrera_display_map = dict(CARRERA_CHOICES)
    carrera_lider = carrera_display_map.get(
        top_carrera_qs['carrera'], 'N/A'
    ) if top_carrera_qs else 'N/A'
    carrera_lider_count = top_carrera_qs['c'] if top_carrera_qs else 0

    # ─── Empresas Pendientes ────────────────────────────────────────────
    empresas_pendientes = Usuario.objects.filter(
        rol='empresa', is_active=False
    ).order_by('-date_joined')

    # ─── Proyectos recientes ────────────────────────────────────────────
    proyectos_recientes = ProyectoGrado.objects.order_by('-fecha_publicacion')[:25]

    # ─── Logs de auditoria ──────────────────────────────────────────────
    logs_recientes = Auditoria.objects.order_by('-fecha')[:50]

    # ─── Chart: Proyectos por mes (ultimos 12 meses) ───────────────────
    twelve_months_ago = now - timedelta(days=365)
    proyectos_por_mes = list(
        ProyectoGrado.objects.filter(
            fecha_publicacion__gte=twelve_months_ago
        ).annotate(
            mes=TruncMonth('fecha_publicacion')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
    )
    chart_meses = json.dumps(
        [p['mes'].strftime('%b %Y') for p in proyectos_por_mes],
        ensure_ascii=False,
    )
    chart_totales = json.dumps([p['total'] for p in proyectos_por_mes])

    # ─── Chart: Proyectos por cluster ──────────────────────────────────
    cluster_display_map = dict(CLUSTER_CHOICES)
    carrera_counts = dict(
        ProyectoGrado.objects.values_list('carrera')
        .annotate(c=Count('id'))
        .values_list('carrera', 'c')
    )
    cluster_agg = {}
    for carrera_key, count in carrera_counts.items():
        cluster_key = CARRERA_A_CLUSTER.get(carrera_key, 'TICS')
        cluster_name = cluster_display_map.get(cluster_key, cluster_key)
        cluster_agg[cluster_name] = cluster_agg.get(cluster_name, 0) + count

    chart_clusters = json.dumps(list(cluster_agg.keys()), ensure_ascii=False)
    chart_cluster_totales = json.dumps(list(cluster_agg.values()))

    # ─── Chart: Empresas registradas por mes (6 meses) ───────────────
    six_months_ago = now - timedelta(days=180)
    empresas_por_mes = list(
        Usuario.objects.filter(
            rol='empresa', date_joined__gte=six_months_ago
        ).annotate(
            mes=TruncMonth('date_joined')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
    )
    chart_empresas_meses = json.dumps(
        [e['mes'].strftime('%b %Y') for e in empresas_por_mes],
        ensure_ascii=False,
    )
    chart_empresas_totales = json.dumps([e['total'] for e in empresas_por_mes])

    # ─── Heatmap: actividad por dia/hora (Auditoria ultimos 30 dias) ──
    thirty_days_ago = now - timedelta(days=30)
    heatmap_raw = list(
        Auditoria.objects.filter(
            fecha__gte=thirty_days_ago
        ).annotate(
            weekday=ExtractWeekDay('fecha'),
            hour=ExtractHour('fecha'),
        ).values('weekday', 'hour').annotate(
            total=Count('id')
        ).order_by('weekday', 'hour')
    )
    # Build 7x24 matrix (Django: 1=Sunday..7=Saturday → remap to 0=Lun..6=Dom)
    django_to_iso = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6}
    heatmap_matrix = [[0] * 24 for _ in range(7)]
    for entry in heatmap_raw:
        day_idx = django_to_iso.get(entry['weekday'], 0)
        heatmap_matrix[day_idx][entry['hour']] = entry['total']
    heatmap_json = json.dumps(heatmap_matrix)

    # ─── Usuarios por rol ────────────────────────────────────────────
    users_by_role = dict(
        Usuario.objects.values_list('rol')
        .annotate(c=Count('id'))
        .values_list('rol', 'c')
    )
    chart_roles = json.dumps(
        ['Aprendices', 'Instructores', 'Empresas', 'Admins'],
        ensure_ascii=False,
    )
    chart_roles_totales = json.dumps([
        users_by_role.get('aprendiz', 0),
        users_by_role.get('instructor', 0),
        users_by_role.get('empresa', 0),
        users_by_role.get('admin', 0),
    ])

    # ─── Network status: intentos fallidos (axes, 7 dias) ────────────
    try:
        from axes.models import AccessAttempt
        seven_days_ago = now - timedelta(days=7)
        failed_logins_7d = AccessAttempt.objects.filter(
            attempt_time__gte=seven_days_ago
        ).count()
        recent_failed = list(
            AccessAttempt.objects.filter(
                attempt_time__gte=seven_days_ago
            ).order_by('-attempt_time').values(
                'username', 'ip_address', 'attempt_time', 'failures_since_start'
            )[:10]
        )
        failed_logins_list = json.dumps([
            {
                'user': f.get('username', '???'),
                'ip': f.get('ip_address', ''),
                'time': f['attempt_time'].strftime('%d/%m %H:%M'),
                'failures': f.get('failures_since_start', 0),
            }
            for f in recent_failed
        ], ensure_ascii=False)
    except Exception:
        failed_logins_7d = 0
        failed_logins_list = '[]'

    # ─── Activity Timeline (ultimas 15 acciones) ─────────────────────
    timeline_entries = list(
        Auditoria.objects.order_by('-fecha')[:15].values(
            'accion', 'tabla', 'registro_id', 'fecha'
        )
    )
    timeline_json = json.dumps([
        {
            'action': t['accion'],
            'model': t['tabla'],
            'id': t['registro_id'],
            'time': t['fecha'].strftime('%d/%m/%Y %H:%M'),
        }
        for t in timeline_entries
    ], ensure_ascii=False)

    # ─── Carreras agrupadas por cluster ────────────────────────────────
    carreras_by_cluster = {}
    for key, label in CARRERA_CHOICES:
        cluster_key = CARRERA_A_CLUSTER.get(key, 'TICS')
        cluster_name = cluster_display_map.get(cluster_key, cluster_key)
        if cluster_name not in carreras_by_cluster:
            carreras_by_cluster[cluster_name] = []
        carreras_by_cluster[cluster_name].append({
            'key': key,
            'label': label,
            'count': carrera_counts.get(key, 0),
        })

    # ─── Logins recientes (ultimos 10 usuarios activos) ────────────────
    logins_recientes = Usuario.objects.filter(
        last_login__isnull=False
    ).order_by('-last_login')[:10]

    # ─── Backup stats ────────────────────────────────────────────────
    from auditoria.models import BackupRecord
    from .backup_utils import get_backup_stats, BACKUP_DIR

    backup_stats = get_backup_stats()
    backup_records = BackupRecord.objects.all()[:20]
    last_backup = backup_stats['last_backup']

    # Check if last backup is > 24h old
    backup_warning = False
    if last_backup:
        hours_since = (now - last_backup.created_at).total_seconds() / 3600
        backup_warning = hours_since > 24
    else:
        backup_warning = True

    return {
        'usuario': user,
        # KPIs
        'total_proyectos_grado': total_proyectos_grado,
        'total_proyectos': total_proyectos,
        'empresas_activas': empresas_activas,
        'total_aprendices': total_aprendices,
        'total_instructores': total_instructores,
        'total_usuarios': total_usuarios,
        # Growth
        'growth_proyectos': growth_proyectos,
        'growth_empresas': growth_empresas,
        'growth_usuarios': growth_usuarios,
        'proyectos_this_month': proyectos_this_month,
        'empresas_this_month': empresas_this_month,
        # Carrera lider
        'carrera_lider': carrera_lider,
        'carrera_lider_count': carrera_lider_count,
        # Moderation
        'empresas_pendientes': empresas_pendientes,
        'empresas_pendientes_count': empresas_pendientes.count(),
        'proyectos_recientes': proyectos_recientes,
        # Audit
        'logs_recientes': logs_recientes,
        'logins_recientes': logins_recientes,
        # Charts - proyectos por mes
        'chart_meses': chart_meses,
        'chart_totales': chart_totales,
        # Charts - clusters
        'chart_clusters': chart_clusters,
        'chart_cluster_totales': chart_cluster_totales,
        # Charts - empresas line
        'chart_empresas_meses': chart_empresas_meses,
        'chart_empresas_totales': chart_empresas_totales,
        # Charts - roles
        'chart_roles': chart_roles,
        'chart_roles_totales': chart_roles_totales,
        # Heatmap
        'heatmap_json': heatmap_json,
        # Network status
        'failed_logins_7d': failed_logins_7d,
        'failed_logins_list': failed_logins_list,
        # Timeline
        'timeline_json': timeline_json,
        # Carreras
        'carreras_by_cluster': carreras_by_cluster,
        # Backups
        'backup_records': backup_records,
        'backup_stats': backup_stats,
        'backup_warning': backup_warning,
    }


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN API ENDPOINTS (AJAX)
# ═══════════════════════════════════════════════════════════════════════════

@admin_required
@require_POST
def admin_aprobar_empresa(request, pk):
    """Aprobar empresa pendiente (activar cuenta)."""
    empresa = get_object_or_404(Usuario, pk=pk, rol='empresa', is_active=False)
    empresa.is_active = True
    empresa.save(update_fields=['is_active'])
    logger.info(f"Empresa aprobada: {empresa.nombre_empresa} (ID={pk}) por {request.user.username}")
    return JsonResponse({'ok': True, 'nombre': empresa.nombre_empresa})


@admin_required
@require_POST
def admin_rechazar_empresa(request, pk):
    """Rechazar (eliminar) empresa pendiente."""

    empresa = get_object_or_404(Usuario, pk=pk, rol='empresa', is_active=False)
    nombre = empresa.nombre_empresa
    empresa.delete()
    logger.info(f"Empresa rechazada: {nombre} (ID={pk}) por {request.user.username}")
    return JsonResponse({'ok': True, 'nombre': nombre})


@admin_required
@require_POST
def admin_toggle_destacado(request, pk):
    """Toggle destacado de un proyecto de grado."""

    from repositorio.models import ProyectoGrado
    proyecto = get_object_or_404(ProyectoGrado, pk=pk)
    proyecto.destacado = not proyecto.destacado
    proyecto.save(update_fields=['destacado'])
    logger.info(f"Proyecto {'destacado' if proyecto.destacado else 'no-destacado'}: {proyecto.titulo} (ID={pk})")
    return JsonResponse({'ok': True, 'destacado': proyecto.destacado})


# ═══════════════════════════════════════════════════════════════════════════
# BACKUP ENDPOINTS (AJAX)
# ═══════════════════════════════════════════════════════════════════════════

@admin_required
@require_POST
def admin_backup_create(request):
    """Crear un nuevo backup (manual)."""

    from auditoria.models import BackupRecord
    from .backup_utils import create_full_backup, create_db_only_backup

    backup_type = request.POST.get('type', 'full')  # full | database
    encrypt = request.POST.get('encrypt', 'false') == 'true'

    try:
        if backup_type == 'database':
            filepath, file_hash, file_size, is_encrypted = create_db_only_backup(encrypt)
            contenido = 'database'
        else:
            filepath, file_hash, file_size, is_encrypted = create_full_backup(encrypt)
            contenido = 'full'

        record = BackupRecord.objects.create(
            filename=filepath.name,
            filepath=str(filepath),
            size_bytes=file_size,
            tipo='manual',
            contenido=contenido,
            hash_sha256=file_hash,
            encrypted=is_encrypted,
            created_by=request.user,
            notes=f'Backup {backup_type} creado por {request.user.username}',
        )

        logger.info(f"Backup creado: {record.filename} por {request.user.username}")

        return JsonResponse({
            'ok': True,
            'id': record.pk,
            'filename': record.filename,
            'size': record.size_display,
            'hash': file_hash[:16] + '...',
            'encrypted': is_encrypted,
            'created_at': record.created_at.strftime('%d/%m/%Y %H:%M'),
        })
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@admin_required
def admin_backup_download(request, pk):
    """Descargar un backup existente."""

    from auditoria.models import BackupRecord
    from pathlib import Path

    record = get_object_or_404(BackupRecord, pk=pk)
    filepath = Path(record.filepath)

    if not filepath.exists():
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)

    response = FileResponse(
        filepath.open('rb'),
        as_attachment=True,
        filename=record.filename,
    )
    logger.info(f"Backup descargado: {record.filename} por {request.user.username}")
    return response


@admin_required
@require_POST
def admin_backup_delete(request, pk):
    """Eliminar un backup."""

    from auditoria.models import BackupRecord
    from .backup_utils import delete_backup_file

    record = get_object_or_404(BackupRecord, pk=pk)
    filename = record.filename
    delete_backup_file(record)
    record.delete()

    logger.info(f"Backup eliminado: {filename} por {request.user.username}")
    return JsonResponse({'ok': True, 'filename': filename})


@admin_required
@require_POST
def admin_backup_restore(request, pk):
    """Restaurar un backup. Requiere confirmacion con contrasena."""

    from auditoria.models import BackupRecord
    from .backup_utils import restore_database, verify_integrity
    from django.contrib.auth import authenticate

    record = get_object_or_404(BackupRecord, pk=pk)

    # Verificar contrasena del admin
    password = request.POST.get('password', '')
    user = authenticate(request, username=request.user.username, password=password)
    if user is None:
        return JsonResponse({
            'error': 'Contrasena incorrecta. La restauracion requiere autenticacion.'
        }, status=403)

    try:
        restore_database(record)
        logger.warning(
            f"BASE DE DATOS RESTAURADA desde {record.filename} "
            f"por {request.user.username}"
        )
        return JsonResponse({
            'ok': True,
            'message': f'Base de datos restaurada desde {record.filename}. '
                       f'Reinicia el servidor para aplicar los cambios.',
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error restaurando backup: {e}")
        return JsonResponse({'error': f'Error en restauracion: {e}'}, status=500)


@admin_required
@require_POST
def admin_backup_verify(request, pk):
    """Verificar integridad de un backup (SHA-256)."""

    from auditoria.models import BackupRecord
    from .backup_utils import verify_integrity
    from pathlib import Path

    record = get_object_or_404(BackupRecord, pk=pk)
    filepath = Path(record.filepath)

    if not filepath.exists():
        return JsonResponse({'error': 'Archivo no encontrado', 'valid': False}, status=404)

    if not record.hash_sha256:
        return JsonResponse({'error': 'No hay hash registrado', 'valid': False}, status=400)

    is_valid = verify_integrity(filepath, record.hash_sha256)
    return JsonResponse({
        'ok': True,
        'valid': is_valid,
        'hash': record.hash_sha256[:16] + '...',
        'message': 'Integridad verificada' if is_valid else 'ALERTA: Hash no coincide',
    })


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN CRUD — PROYECTOS
# ═══════════════════════════════════════════════════════════════════════════

@admin_required
@require_http_methods(["GET", "POST"])
def admin_proyecto_form(request, pk=None):
    """Create or edit a ProyectoGrado."""
    from repositorio.models import ProyectoGrado, Carrera, CLUSTER_CHOICES
    from repositorio.forms import ProyectoGradoAdminForm

    proyecto = get_object_or_404(ProyectoGrado, pk=pk) if pk else None

    if request.method == 'POST':
        form = ProyectoGradoAdminForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            obj = form.save(commit=False)
            if not pk:
                obj.subido_por = request.user
            obj.save()
            form.save_m2m()
            logger.info(
                f"Proyecto {'editado' if pk else 'creado'}: {obj.titulo} "
                f"(ID={obj.pk}) por {request.user.username}"
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'id': obj.pk, 'titulo': obj.titulo})
            messages.success(request, f'Proyecto {"actualizado" if pk else "creado"} exitosamente.')
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = ProyectoGradoAdminForm(instance=proyecto)

    # Group carreras by cluster for the dropdown
    cluster_map = dict(CLUSTER_CHOICES)
    carreras = Carrera.objects.filter(activa=True).order_by('cluster', 'orden', 'nombre')
    carreras_by_cluster = {}
    for c in carreras:
        cluster_label = cluster_map.get(c.cluster, c.cluster)
        carreras_by_cluster.setdefault(cluster_label, []).append(c)

    return render(request, 'admin/proyecto_form.html', {
        'form': form,
        'proyecto': proyecto,
        'is_edit': pk is not None,
        'carreras_by_cluster': carreras_by_cluster,
    })


@admin_required
@require_POST
def admin_proyecto_delete(request, pk):
    """Delete a ProyectoGrado."""
    from repositorio.models import ProyectoGrado

    proyecto = get_object_or_404(ProyectoGrado, pk=pk)
    titulo = proyecto.titulo
    proyecto.delete()
    logger.info(f"Proyecto eliminado: {titulo} (ID={pk}) por {request.user.username}")
    return JsonResponse({'ok': True, 'titulo': titulo})


@admin_required
def admin_buscar_aprendiz(request):
    """Search Aprendiz by name, document, or email. Returns top 10 as JSON."""
    from aprendices.models import Aprendiz
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    aprendices = Aprendiz.objects.filter(
        Q(nombres__icontains=q) |
        Q(apellidos__icontains=q) |
        Q(numero_documento__icontains=q) |
        Q(email__icontains=q)
    )[:10]

    results = [
        {
            'id': a.pk,
            'nombre': f'{a.nombres} {a.apellidos}',
            'documento': a.numero_documento,
            'email': a.email,
            'telefono': a.telefono,
        }
        for a in aprendices
    ]
    return JsonResponse({'results': results})


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN CRUD — CARRERAS
# ═══════════════════════════════════════════════════════════════════════════

@admin_required
def admin_carreras_list(request):
    """List all carreras grouped by cluster."""
    from repositorio.models import Carrera, CLUSTER_CHOICES

    cluster_map = dict(CLUSTER_CHOICES)
    carreras = Carrera.objects.all().order_by('cluster', 'orden', 'nombre')
    carreras_by_cluster = {}
    for c in carreras:
        cluster_label = cluster_map.get(c.cluster, c.cluster)
        carreras_by_cluster.setdefault(cluster_label, []).append(c)

    return render(request, 'admin/carreras_list.html', {
        'carreras_by_cluster': carreras_by_cluster,
        'total_carreras': carreras.count(),
    })


@admin_required
@require_http_methods(["GET", "POST"])
def admin_carrera_form(request, pk=None):
    """Create or edit a Carrera."""
    from repositorio.models import Carrera
    from repositorio.forms import CarreraAdminForm

    carrera = get_object_or_404(Carrera, pk=pk) if pk else None

    if request.method == 'POST':
        form = CarreraAdminForm(request.POST, instance=carrera)
        if form.is_valid():
            obj = form.save()
            logger.info(
                f"Carrera {'editada' if pk else 'creada'}: {obj.nombre} "
                f"(ID={obj.pk}) por {request.user.username}"
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'id': obj.pk, 'nombre': obj.nombre})
            messages.success(request, f'Carrera {"actualizada" if pk else "creada"} exitosamente.')
            return redirect('admin_carreras_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = CarreraAdminForm(instance=carrera)

    return render(request, 'admin/carrera_form.html', {
        'form': form,
        'carrera': carrera,
        'is_edit': pk is not None,
    })


@admin_required
@require_POST
def admin_carrera_delete(request, pk):
    """Delete a Carrera."""
    from repositorio.models import Carrera

    carrera = get_object_or_404(Carrera, pk=pk)
    nombre = carrera.nombre
    carrera.delete()
    logger.info(f"Carrera eliminada: {nombre} (ID={pk}) por {request.user.username}")
    return JsonResponse({'ok': True, 'nombre': nombre})


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN — EMPRESA DETALLE
# ═══════════════════════════════════════════════════════════════════════════

@admin_required
def admin_empresa_detalle(request, pk):
    """Full detail view for enterprise validation."""
    empresa = get_object_or_404(Usuario, pk=pk, rol='empresa')
    return render(request, 'admin/empresa_detalle.html', {
        'empresa': empresa,
    })


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _calc_growth(current, previous):
    """Calcula porcentaje de crecimiento entre dos periodos."""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100)


