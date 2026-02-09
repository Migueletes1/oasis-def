from rest_framework import viewsets
from .models import Instructor
from .serializers import InstructorSerializer


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'especialidad']
    ordering_fields = ['nombres', 'apellidos', 'especialidad']
    ordering = ['apellidos']
