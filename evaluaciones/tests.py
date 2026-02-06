from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from asignaciones.models import Asignacion
from proyectos.models import Proyecto
from aprendices.models import Aprendiz
from empresas.models import Empresa

class EvaluacionTests(APITestCase):
    def setUp(self):
        empresa = Empresa.objects.create(nit='3', nombre='E', direccion='D', telefono='3')
        proyecto = Proyecto.objects.create(codigo='P3', nombre='P3', descripcion='D', fecha_inicio='2024-01-01', fecha_fin='2024-12-31', empresa=empresa)
        aprendiz = Aprendiz.objects.create(tipo_documento='CC', numero_documento='3', nombres='A', apellidos='P', email='c@c.com', telefono='3')
        self.asignacion = Asignacion.objects.create(proyecto=proyecto, aprendiz=aprendiz, fecha_inicio='2024-01-01', fecha_fin='2024-06-30')
        self.url = reverse('evaluacion_list_create')

    def test_create_evaluacion(self):
        data = {
            'asignacion': self.asignacion.id,
            'calificacion': '4.50',
            'observaciones': 'Excelente'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
