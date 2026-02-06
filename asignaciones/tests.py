from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Asignacion
from proyectos.models import Proyecto
from aprendices.models import Aprendiz
from empresas.models import Empresa
import datetime

class AsignacionTests(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nit='1', nombre='Emp', direccion='Dir', telefono='1')
        self.proyecto = Proyecto.objects.create(
            codigo='P1', nombre='Proj1', descripcion='D', 
            fecha_inicio='2024-01-01', fecha_fin='2024-12-31', empresa=self.empresa
        )
        self.aprendiz = Aprendiz.objects.create(
            tipo_documento='CC', numero_documento='1', nombres='A', apellidos='P', 
            email='a@a.com', telefono='1'
        )
        self.url = reverse('asignacion_list_create')
        self.data = {
            'proyecto': self.proyecto.id,
            'aprendiz': self.aprendiz.id,
            'fecha_inicio': '2024-02-01',
            'fecha_fin': '2024-06-30'
        }

    def test_create_asignacion(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asignacion.objects.count(), 1)

    def test_duplicate_active_asignacion_fails(self):
        # Create first assignment
        self.client.post(self.url, self.data, format='json')
        
        # Try to create identical active assignment
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
