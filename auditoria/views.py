from rest_framework import serializers, viewsets
from .models import Auditoria

class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = '__all__'

class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.all().order_by('-fecha')
    serializer_class = AuditoriaSerializer
