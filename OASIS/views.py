import json
import logging

from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render

from repositorio.models import (
    ProyectoGrado, CARRERA_CHOICES, CLUSTER_CHOICES, CARRERA_A_CLUSTER,
)

logger = logging.getLogger(__name__)

# Icono FontAwesome y color por cluster
CLUSTER_META = {
    'TICS':       {'icon': 'fa-microchip',         'color': 'emerald'},
    'ADMIN':      {'icon': 'fa-briefcase',          'color': 'blue'},
    'SALUD':      {'icon': 'fa-heart-pulse',        'color': 'rose'},
    'INDUSTRIAL': {'icon': 'fa-gear',               'color': 'amber'},
    'CREATIVAS':  {'icon': 'fa-palette',            'color': 'violet'},
    'AGRO':       {'icon': 'fa-leaf',               'color': 'lime'},
    'TURISMO':    {'icon': 'fa-utensils',           'color': 'orange'},
}

# Icono especifico por carrera
CARRERA_ICONS = {
    'software': 'fa-code', 'animacion_3d': 'fa-cube', 'adsi': 'fa-laptop-code',
    'multimedia': 'fa-photo-film', 'redes': 'fa-network-wired',
    'telecomunicaciones': 'fa-tower-cell', 'videojuegos': 'fa-gamepad',
    'ia': 'fa-robot', 'ciberseguridad': 'fa-shield-halved',
    'ciencia_datos': 'fa-chart-line',
    'contabilidad': 'fa-calculator', 'gestion_admin': 'fa-clipboard-list',
    'talento_humano': 'fa-users', 'gestion_empresarial': 'fa-building',
    'negocios_int': 'fa-globe', 'logistica': 'fa-truck-fast',
    'bancaria': 'fa-landmark', 'mercados': 'fa-bullhorn',
    'comercio_int': 'fa-ship',
    'enfermeria': 'fa-user-nurse', 'salud_ocup': 'fa-helmet-safety',
    'farmacia': 'fa-pills', 'primera_infancia': 'fa-baby',
    'sst': 'fa-hard-hat', 'nutricion': 'fa-apple-whole',
    'imagenes_dx': 'fa-x-ray',
    'electricidad': 'fa-bolt', 'electronica': 'fa-microchip',
    'mecanica': 'fa-wrench', 'automatizacion': 'fa-industry',
    'electromecanica': 'fa-screwdriver-wrench', 'construccion': 'fa-helmet-safety',
    'mecatronica': 'fa-gears', 'diseno_industrial': 'fa-compass-drafting',
    'diseno_grafico': 'fa-pen-nib', 'audiovisual': 'fa-video',
    'comunicacion': 'fa-comments', 'fotografia': 'fa-camera',
    'modas': 'fa-shirt',
    'ambiental': 'fa-tree', 'agroindustria': 'fa-wheat-awn',
    'agropecuaria': 'fa-tractor',
    'gastronomia': 'fa-utensils', 'hotelera': 'fa-hotel',
}


def index(request):
    carreras_data = []
    for key, label in CARRERA_CHOICES:
        cluster = CARRERA_A_CLUSTER.get(key, 'TICS')
        meta = CLUSTER_META.get(cluster, {})
        carreras_data.append({
            'key': key,
            'label': label,
            'cluster': cluster,
            'cluster_display': dict(CLUSTER_CHOICES).get(cluster, cluster),
            'icon': CARRERA_ICONS.get(key, 'fa-graduation-cap'),
            'color': meta.get('color', 'emerald'),
        })

    proyectos_destacados = list(
        ProyectoGrado.objects.filter(destacado=True)
        .order_by('-votos', '-fecha_publicacion')[:5]
        .values('id', 'titulo', 'descripcion', 'carrera', 'autor', 'votos', 'imagen_url', 'enlace_repositorio')
    )

    clusters_data = []
    for key, label in CLUSTER_CHOICES:
        meta = CLUSTER_META.get(key, {})
        count = sum(1 for c in CARRERA_CHOICES if CARRERA_A_CLUSTER.get(c[0]) == key)
        clusters_data.append({
            'key': key,
            'label': label,
            'icon': meta.get('icon', 'fa-folder'),
            'color': meta.get('color', 'emerald'),
            'count': count,
        })

    context = {
        'carreras': carreras_data,
        'carreras_json': json.dumps(carreras_data),
        'clusters': clusters_data,
        'proyectos_destacados': proyectos_destacados,
        'proyectos_json': json.dumps(proyectos_destacados, default=str),
        'total_carreras': len(CARRERA_CHOICES),
    }
    return render(request, 'index.html', context)


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'ok', 'database': 'connected'}, status=200)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({'status': 'error', 'database': 'unavailable'}, status=503)
