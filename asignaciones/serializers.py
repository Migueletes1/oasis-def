from rest_framework import serializers
from .models import Asignacion

class AsignacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignacion
        fields = '__all__'
        
    def validate(self, data):
        # Validate that the apprentice is not already assigned to this project actively
        # Only on creation (no instance) or if changing values
        if not self.instance:
            proyecto = data.get('proyecto')
            aprendiz = data.get('aprendiz')
            activo = data.get('activo', True)
            
            if activo and Asignacion.objects.filter(proyecto=proyecto, aprendiz=aprendiz, activo=True).exists():
                raise serializers.ValidationError("El aprendiz ya tiene una asignación activa en este proyecto.")
        return data
