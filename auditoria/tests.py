from rest_framework.test import APITestCase
from empresas.models import Empresa
from auditoria.models import Auditoria

class AuditoriaTests(APITestCase):
    def test_audit_log_created(self):
        # Action that triggers signal
        empresa = Empresa.objects.create(
            nit='999',
            nombre='Audit Test',
            direccion='Audit Dir',
            telefono='999'
        )
        
        # Verify audit log
        log = Auditoria.objects.filter(tabla='empresa', registro_id=empresa.id).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.accion, 'CREATE')
