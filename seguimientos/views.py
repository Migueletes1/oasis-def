from rest_framework import serializers, viewsets
from .models import Seguimiento

class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'

class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.select_related('asignacion').all()
    serializer_class = SeguimientoSerializer
