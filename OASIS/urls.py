from django.contrib import admin
from django.urls import path, include

from .views import health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('api/v1/', include('OASIS.api_urls')),
    
    # Legacy Endpoints (Left intact as per instructions to not break existing)
    path('api/proyectos/', include('proyectos.urls')),
    path('api/empresas/', include('empresas.urls')),
    path('api/aprendices/', include('aprendices.urls')),
    path('api/instructores/', include('instructores.urls')),
    path('api/asignaciones/', include('asignaciones.urls')),
    path('api/seguimientos/', include('seguimientos.urls')),
    path('api/evaluaciones/', include('evaluaciones.urls')),
    path('api/reportes/', include('reportes.urls')),
]
