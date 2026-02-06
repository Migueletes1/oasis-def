from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Proyecto
from empresas.models import Empresa
import datetime

class ProyectoTests(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nit='111222333',
            nombre='Empresa Test',
            direccion='Calle Test',
            telefono='555555'
        )
        self.proyecto_data = {
            'codigo': 'PROJ-001',
            'nombre': 'Sistema de Gestion',
            'descripcion': 'Desarrollo web',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-06-30',
            'empresa': self.empresa.id  # Send ID for FK
        }
        self.list_url = reverse('proyecto_list_create')
        
    def test_create_proyecto(self):
        response = self.client.post(self.list_url, self.proyecto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Proyecto.objects.count(), 1)
        self.assertEqual(Proyecto.objects.get().codigo, 'PROJ-001')

    def test_create_proyecto_missing_field(self):
        data = self.proyecto_data.copy()
        del data['codigo']
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
