from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import index, health_check

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    # Auth (sesiones web)
    path('auth/', include('usuarios.urls')),

    # JWT Authentication (API)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API v1 (canonical)
    path('api/v1/', include('OASIS.api_urls')),

    # Repositorio (public-facing)
    path('repositorio/', include('repositorio.urls')),

    # Legacy Endpoints (deprecated - usar /api/v1/ en su lugar)
    path('api/proyectos/', include('proyectos.urls')),
    path('api/empresas/', include('empresas.urls')),
    path('api/aprendices/', include('aprendices.urls')),
    path('api/instructores/', include('instructores.urls')),
    path('api/asignaciones/', include('asignaciones.urls')),
    path('api/seguimientos/', include('seguimientos.urls')),
    path('api/evaluaciones/', include('evaluaciones.urls')),
    path('api/reportes/', include('reportes.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
