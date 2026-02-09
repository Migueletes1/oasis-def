from rest_framework import viewsets
from .models import Proyecto
from .serializers import ProyectoSerializer


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.select_related('empresa').all()
    serializer_class = ProyectoSerializer
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'fecha_inicio', 'fecha_fin']
    ordering = ['nombre']
