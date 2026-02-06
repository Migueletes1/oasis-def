from rest_framework.routers import DefaultRouter
from proyectos.views import ProyectoViewSet
from empresas.views import EmpresaViewSet
from aprendices.views import AprendizViewSet
from instructores.views import InstructorViewSet
from asignaciones.views import AsignacionViewSet
from seguimientos.views import SeguimientoViewSet
from evaluaciones.views import EvaluacionViewSet
from auditoria.views import AuditoriaViewSet
from reportes.views import ReporteViewSet

router = DefaultRouter()
router.register(r'proyectos', ProyectoViewSet)
router.register(r'empresas', EmpresaViewSet)
router.register(r'aprendices', AprendizViewSet)
router.register(r'instructores', InstructorViewSet)
router.register(r'asignaciones', AsignacionViewSet)
router.register(r'seguimientos', SeguimientoViewSet)
router.register(r'evaluaciones', EvaluacionViewSet)
router.register(r'auditoria', AuditoriaViewSet)
router.register(r'reportes', ReporteViewSet, basename='reportes')

urlpatterns = router.urls
