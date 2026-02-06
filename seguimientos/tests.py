from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from asignaciones.models import Asignacion
from proyectos.models import Proyecto
from aprendices.models import Aprendiz
from empresas.models import Empresa

class SeguimientoTests(APITestCase):
    def setUp(self):
        empresa = Empresa.objects.create(nit='2', nombre='E', direccion='D', telefono='2')
        proyecto = Proyecto.objects.create(codigo='P2', nombre='P2', descripcion='D', fecha_inicio='2024-01-01', fecha_fin='2024-12-31', empresa=empresa)
        aprendiz = Aprendiz.objects.create(tipo_documento='CC', numero_documento='2', nombres='A', apellidos='P', email='b@b.com', telefono='2')
        self.asignacion = Asignacion.objects.create(proyecto=proyecto, aprendiz=aprendiz, fecha_inicio='2024-01-01', fecha_fin='2024-06-30')
        self.url = reverse('seguimiento_list_create')

    def test_create_seguimiento(self):
        data = {
            'asignacion': self.asignacion.id,
            'observaciones': 'Avance ok',
            'estado': 'En proceso'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
