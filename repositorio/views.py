import hashlib
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from OASIS.utils import get_client_ip
from .models import (
    ProyectoGrado, ArchivoProyecto, TagHabilidad, RegistroDescarga,
    CARRERA_CHOICES, CLUSTER_CHOICES, CARRERA_A_CLUSTER, CARRERA_A_PREVIEW,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# EXPLORADOR — Card Grid with Faceted Search
# ═══════════════════════════════════════════════════════════════════════════

def explorador(request):
    """Public repository explorer with faceted search and card grid."""
    qs = ProyectoGrado.objects.filter(
        estado=ProyectoGrado.EstadoProyecto.PUBLICADO
    ).select_related('instructor_avalador', 'subido_por').prefetch_related('tags', 'archivos')

    # ── Search ──
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(titulo__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(autor__icontains=q) |
            Q(herramientas_usadas__icontains=q) |
            Q(ficha__icontains=q)
        )

    # ── Filters ──
    carrera = request.GET.get('carrera', '')
    if carrera:
        qs = qs.filter(carrera=carrera)

    cluster = request.GET.get('cluster', '')
    if cluster:
        carreras_in_cluster = [k for k, v in CARRERA_A_CLUSTER.items() if v == cluster]
        qs = qs.filter(carrera__in=carreras_in_cluster)

    anio = request.GET.get('anio', '')
    if anio:
        try:
            qs = qs.filter(anio=int(anio))
        except ValueError:
            pass

    tag = request.GET.get('tag', '')
    if tag:
        qs = qs.filter(tags__slug=tag)

    preview_type = request.GET.get('tipo', '')
    if preview_type:
        carreras_with_type = [k for k, v in CARRERA_A_PREVIEW.items() if v == preview_type]
        qs = qs.filter(carrera__in=carreras_with_type)

    # ── Sort ──
    sort = request.GET.get('sort', 'recientes')
    sort_map = {
        'recientes': '-fecha_publicacion',
        'populares': '-votos',
        'descargas': '-descargas',
        'titulo': 'titulo',
    }
    qs = qs.order_by(sort_map.get(sort, '-fecha_publicacion'))

    # ── Stats for sidebar (single query instead of N+1 per cluster) ──
    total_count = qs.count()
    all_published = ProyectoGrado.objects.filter(estado=ProyectoGrado.EstadoProyecto.PUBLICADO)
    carrera_counts = dict(
        all_published.values_list('carrera').annotate(c=Count('id')).values_list('carrera', 'c')
    )
    cluster_display = dict(CLUSTER_CHOICES)
    stats_by_cluster = {}
    for carrera_key, count in carrera_counts.items():
        ckey = CARRERA_A_CLUSTER.get(carrera_key, 'TICS')
        if ckey not in stats_by_cluster:
            stats_by_cluster[ckey] = {'name': cluster_display.get(ckey, ckey), 'count': 0}
        stats_by_cluster[ckey]['count'] += count

    available_years = (
        all_published
        .values_list('anio', flat=True)
        .distinct()
        .order_by('-anio')
    )

    popular_tags = (
        TagHabilidad.objects
        .filter(proyectos__estado=ProyectoGrado.EstadoProyecto.PUBLICADO)
        .annotate(num_proyectos=Count('proyectos'))
        .order_by('-num_proyectos')[:20]
    )

    context = {
        'proyectos': qs[:60],
        'total_count': total_count,
        'query': q,
        'selected_carrera': carrera,
        'selected_cluster': cluster,
        'selected_anio': anio,
        'selected_tag': tag,
        'selected_tipo': preview_type,
        'selected_sort': sort,
        'carrera_choices': CARRERA_CHOICES,
        'cluster_choices': CLUSTER_CHOICES,
        'stats_by_cluster': stats_by_cluster,
        'available_years': available_years,
        'popular_tags': popular_tags,
    }
    return render(request, 'repositorio/explorador.html', context)


# ═══════════════════════════════════════════════════════════════════════════
# DETALLE — Smart Preview per Career Type
# ═══════════════════════════════════════════════════════════════════════════

def proyecto_detalle(request, pk):
    """Project detail with career-specific smart preview."""
    proyecto = get_object_or_404(
        ProyectoGrado.objects.select_related('instructor_avalador', 'subido_por')
        .prefetch_related('tags', 'archivos'),
        pk=pk,
    )

    # Increment views
    ProyectoGrado.objects.filter(pk=pk).update(vistas=F('vistas') + 1)

    archivos = proyecto.archivos.all()
    archivos_by_version = {}
    for a in archivos:
        v = a.get_version_label_display()
        archivos_by_version.setdefault(v, []).append(a)

    # Separate file types for smart preview
    images = archivos.filter(tipo='imagen')
    code_files = archivos.filter(tipo='codigo')
    documents = archivos.filter(tipo='documento')
    videos = archivos.filter(tipo='video')
    models_3d = archivos.filter(tipo='modelo_3d')

    # Related projects (same career, excluding current)
    related = (
        ProyectoGrado.objects
        .filter(carrera=proyecto.carrera, estado=ProyectoGrado.EstadoProyecto.PUBLICADO)
        .exclude(pk=pk)
        .order_by('-votos')[:4]
    )

    can_edit = False
    can_download = True
    if request.user.is_authenticated:
        user = request.user
        can_edit = (
            user.es_admin or
            user == proyecto.subido_por or
            user == proyecto.instructor_avalador
        )
        # All authenticated users can download
        can_download = True
    else:
        # Anonymous users can only view, not download
        can_download = False

    context = {
        'proyecto': proyecto,
        'archivos': archivos,
        'archivos_by_version': archivos_by_version,
        'images': images,
        'code_files': code_files,
        'documents': documents,
        'videos': videos,
        'models_3d': models_3d,
        'related': related,
        'can_edit': can_edit,
        'can_download': can_download,
        'preview_type': proyecto.preview_type,
    }
    return render(request, 'repositorio/detalle.html', context)


# ═══════════════════════════════════════════════════════════════════════════
# DOWNLOAD — Role-Based with Audit Trail
# ═══════════════════════════════════════════════════════════════════════════

@login_required
def descargar_archivo(request, archivo_id):
    """Download a project file with permission check and audit logging."""
    archivo = get_object_or_404(ArchivoProyecto.objects.select_related('proyecto'), pk=archivo_id)

    # Log the download
    RegistroDescarga.objects.create(
        archivo=archivo,
        usuario=request.user,
        ip_address=get_client_ip(request),
    )

    # Increment download counter on the project
    ProyectoGrado.objects.filter(pk=archivo.proyecto_id).update(descargas=F('descargas') + 1)

    response = FileResponse(archivo.archivo.open('rb'), as_attachment=True,
                            filename=archivo.nombre_original)
    return response


# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD — Version-Aware File Upload
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@require_POST
def subir_archivos(request, pk):
    """Upload files to a project (owners, instructors, admins)."""
    proyecto = get_object_or_404(ProyectoGrado, pk=pk)

    user = request.user
    if not (user.es_admin or user == proyecto.subido_por or user == proyecto.instructor_avalador):
        return JsonResponse({'error': 'No tienes permisos para subir archivos a este proyecto.'}, status=403)

    files = request.FILES.getlist('archivos')
    if not files:
        return JsonResponse({'error': 'No se seleccionaron archivos.'}, status=400)

    version_label = request.POST.get('version', ProyectoGrado.VersionLabel.V1)
    if version_label not in dict(ProyectoGrado.VersionLabel.choices):
        version_label = ProyectoGrado.VersionLabel.V1

    created = []
    for f in files:
        # Hash the file
        sha256 = hashlib.sha256()
        for chunk in f.chunks():
            sha256.update(chunk)
        file_hash = sha256.hexdigest()
        f.seek(0)  # Reset file pointer after hashing

        archivo = ArchivoProyecto(
            proyecto=proyecto,
            archivo=f,
            nombre_original=f.name,
            size_bytes=f.size,
            hash_sha256=file_hash,
            version_label=version_label,
            subido_por=user,
        )
        archivo.tipo = archivo.detect_tipo()

        # Simulated anti-malware scan
        suspicious_extensions = ['exe', 'bat', 'cmd', 'com', 'scr', 'pif', 'vbs', 'msi']
        if archivo.extension in suspicious_extensions:
            archivo.scan_status = 'suspicious'
        else:
            archivo.scan_status = 'clean'

        archivo.save()
        created.append({
            'id': archivo.pk,
            'name': archivo.nombre_original,
            'size': archivo.size_display,
            'type': archivo.tipo,
            'scan': archivo.scan_status,
        })

    return JsonResponse({
        'ok': True,
        'message': f'{len(created)} archivo(s) subidos correctamente.',
        'archivos': created,
    })


# ═══════════════════════════════════════════════════════════════════════════
# VOTE — Ajax voting
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@require_POST
def votar_proyecto(request, pk):
    """Vote for a project (one vote per user, stored in session)."""
    proyecto = get_object_or_404(ProyectoGrado, pk=pk)

    voted_key = f'voted_{pk}'
    if request.session.get(voted_key):
        return JsonResponse({'ok': False, 'error': 'Ya votaste por este proyecto.', 'votos': proyecto.votos})

    ProyectoGrado.objects.filter(pk=pk).update(votos=F('votos') + 1)
    request.session[voted_key] = True
    proyecto.refresh_from_db()
    return JsonResponse({'ok': True, 'votos': proyecto.votos})
