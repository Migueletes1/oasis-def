from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Aprendiz

class AprendizTests(APITestCase):
    def setUp(self):
        self.aprendiz_data = {
            'tipo_documento': 'CC',
            'numero_documento': '123456789',
            'nombres': 'Juan',
            'apellidos': 'Perez',
            'email': 'juan.perez@example.com',
            'telefono': '3001112233'
        }
        self.list_url = reverse('aprendiz_list_create')
        
    def test_create_aprendiz(self):
        response = self.client.post(self.list_url, self.aprendiz_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Aprendiz.objects.count(), 1)

    def test_create_duplicate_aprendiz_fails(self):
        self.client.post(self.list_url, self.aprendiz_data, format='json')
        response = self.client.post(self.list_url, self.aprendiz_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
