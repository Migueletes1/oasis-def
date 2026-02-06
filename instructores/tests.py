from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Instructor

class InstructorTests(APITestCase):
    def setUp(self):
        self.instructor_data = {
            'tipo_documento': 'CC',
            'numero_documento': '987654321',
            'nombres': 'Maria',
            'apellidos': 'Gonzalez',
            'email': 'maria.gonzalez@example.com',
            'especialidad': 'Software'
        }
        self.list_url = reverse('instructor_list_create')

    def test_create_instructor(self):
        response = self.client.post(self.list_url, self.instructor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Instructor.objects.count(), 1)
