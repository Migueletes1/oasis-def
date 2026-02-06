from rest_framework import viewsets
from .models import Aprendiz
from .serializers import AprendizSerializer

class AprendizViewSet(viewsets.ModelViewSet):
    queryset = Aprendiz.objects.all()
    serializer_class = AprendizSerializer
