from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from asignaciones.models import Asignacion
from proyectos.models import Proyecto
from aprendices.models import Aprendiz
from empresas.models import Empresa

class ReporteTests(APITestCase):
    def setUp(self):
        empresa = Empresa.objects.create(nit='R', nombre='ER', direccion='DR', telefono='R')
        proyecto = Proyecto.objects.create(codigo='PR', nombre='PR', descripcion='D', fecha_inicio='2024-01-01', fecha_fin='2024-12-31', empresa=empresa)
        aprendiz = Aprendiz.objects.create(tipo_documento='CC', numero_documento='R', nombres='A', apellidos='P', email='r@r.com', telefono='R')
        Asignacion.objects.create(proyecto=proyecto, aprendiz=aprendiz, fecha_inicio='2024-01-01', fecha_fin='2024-06-30')
        self.url = reverse('reporte_asignaciones')

    def test_get_reporte_asignaciones(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['proyecto_codigo'], 'PR')
