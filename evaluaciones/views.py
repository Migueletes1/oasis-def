from rest_framework import serializers, viewsets
from .models import Evaluacion

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'

class EvaluacionViewSet(viewsets.ModelViewSet):
    queryset = Evaluacion.objects.select_related('asignacion').all()
    serializer_class = EvaluacionSerializer
