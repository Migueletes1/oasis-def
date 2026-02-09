from rest_framework import viewsets
from .models import Evaluacion
from .serializers import EvaluacionSerializer


class EvaluacionViewSet(viewsets.ModelViewSet):
    queryset = Evaluacion.objects.select_related('asignacion').all()
    serializer_class = EvaluacionSerializer
    search_fields = ['observaciones']
    ordering_fields = ['fecha', 'calificacion']
    ordering = ['-fecha']
