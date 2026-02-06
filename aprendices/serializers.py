from rest_framework import serializers
from .models import Aprendiz

class AprendizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aprendiz
        fields = '__all__'
