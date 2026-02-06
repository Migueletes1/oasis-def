from rest_framework import viewsets
from .models import Asignacion
from .serializers import AsignacionSerializer

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.select_related('proyecto', 'aprendiz', 'instructor').all()
    serializer_class = AsignacionSerializer
