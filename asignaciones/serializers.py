from django.db import IntegrityError
from rest_framework import serializers
from .models import Asignacion


class AsignacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignacion
        fields = '__all__'

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })

        if not self.instance:
            proyecto = data.get('proyecto')
            aprendiz = data.get('aprendiz')
            activo = data.get('activo', True)

            if activo and Asignacion.objects.filter(
                proyecto=proyecto, aprendiz=aprendiz, activo=True
            ).exists():
                raise serializers.ValidationError(
                    "El aprendiz ya tiene una asignacion activa en este proyecto."
                )
        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                "El aprendiz ya tiene una asignacion activa en este proyecto."
            )
