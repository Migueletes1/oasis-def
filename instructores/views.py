from rest_framework import viewsets
from .models import Instructor
from .serializers import InstructorSerializer

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
