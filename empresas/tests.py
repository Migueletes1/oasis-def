from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Empresa

class EmpresaTests(APITestCase):
    def setUp(self):
        self.empresa_data = {
            'nit': '900123456',
            'nombre': 'Tech Solutions SAS',
            'direccion': 'Calle 123',
            'telefono': '3001234567'
        }
        self.empresa = Empresa.objects.create(**self.empresa_data)
        self.list_url = reverse('empresa_list_create')
        self.detail_url = reverse('empresa_detail_update_delete', args=[self.empresa.id])

    def test_create_empresa(self):
        data = {
            'nit': '800987654',
            'nombre': 'Innovatech',
            'direccion': 'Carrera 45',
            'telefono': '3109876543'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empresa.objects.count(), 2)

    def test_get_empresas(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_empresa(self):
        data = {'nombre': 'Tech Solutions Updated'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.nombre, 'Tech Solutions Updated')

    def test_delete_empresa(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Empresa.objects.count(), 0)
