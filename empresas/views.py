from rest_framework import viewsets
from .models import Empresa
from .serializers import EmpresaSerializer


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    search_fields = ['nombre', 'nit']
    ordering_fields = ['nombre', 'nit']
    ordering = ['nombre']
