from rest_framework import viewsets
from .models import Asignacion
from .serializers import AsignacionSerializer


class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.select_related('proyecto', 'aprendiz', 'instructor').all()
    serializer_class = AsignacionSerializer
    search_fields = ['proyecto__nombre', 'aprendiz__nombres', 'aprendiz__apellidos']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'activo']
    ordering = ['-fecha_inicio']
