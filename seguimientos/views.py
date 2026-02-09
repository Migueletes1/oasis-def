from rest_framework import viewsets
from .models import Seguimiento
from .serializers import SeguimientoSerializer


class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.select_related('asignacion').all()
    serializer_class = SeguimientoSerializer
    search_fields = ['estado', 'observaciones']
    ordering_fields = ['fecha', 'estado']
    ordering = ['-fecha']
