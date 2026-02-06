from django.urls import path
from .views import ReporteViewSet

reporte_asignaciones = ReporteViewSet.as_view({
    'get': 'list'
})

urlpatterns = [
    path('asignaciones/', reporte_asignaciones, name='reporte_asignaciones'),
]
