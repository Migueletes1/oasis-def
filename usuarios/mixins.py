import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class RolRequeridoMixin(LoginRequiredMixin):
    """
    Mixin RBAC para Class-Based Views.

    Uso:
        class MiVista(RolRequeridoMixin, TemplateView):
            roles_permitidos = ['admin', 'instructor']
    """
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return response
        if request.user.is_superuser:
            return response
        if self.roles_permitidos and request.user.rol not in self.roles_permitidos:
            logger.warning(
                f"RBAC denegado: usuario={request.user.username} "
                f"rol={request.user.rol} vs permitidos={self.roles_permitidos}"
            )
            raise PermissionDenied('No tienes permisos para acceder a esta seccion.')
        return response


class SoloAdminMixin(RolRequeridoMixin):
    roles_permitidos = ['admin']


class SoloEmpresaMixin(RolRequeridoMixin):
    roles_permitidos = ['empresa']


class SoloInstructorMixin(RolRequeridoMixin):
    roles_permitidos = ['instructor']


class SoloAprendizMixin(RolRequeridoMixin):
    roles_permitidos = ['aprendiz']
