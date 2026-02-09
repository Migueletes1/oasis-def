import functools
import logging

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def rol_requerido(*roles_permitidos):
    """
    Decorador RBAC que restringe acceso a vistas por rol.

    Uso:
        @rol_requerido('admin')
        @rol_requerido('empresa', 'admin')
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.rol not in roles_permitidos:
                logger.warning(
                    f"Acceso denegado: usuario={request.user.username} "
                    f"rol={request.user.rol} intento acceder a vista "
                    f"restringida a {roles_permitidos}"
                )
                return HttpResponseForbidden(
                    '<h1>403 - Acceso Denegado</h1>'
                    '<p>No tienes permisos para acceder a esta seccion.</p>'
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_admin(view_func):
    """Atajo: solo administradores."""
    return rol_requerido('admin')(view_func)


def solo_empresa(view_func):
    """Atajo: solo empresas (activas)."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.rol == 'empresa' or request.user.is_superuser):
            return HttpResponseForbidden(
                '<h1>403 - Acceso Denegado</h1>'
                '<p>Esta seccion es exclusiva para empresas.</p>'
            )
        if not request.user.is_active:
            return HttpResponseForbidden(
                '<h1>Cuenta Pendiente</h1>'
                '<p>Tu cuenta de empresa aun no ha sido aprobada por un administrador.</p>'
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_instructor(view_func):
    """Atajo: solo instructores."""
    return rol_requerido('instructor')(view_func)


def solo_aprendiz(view_func):
    """Atajo: solo aprendices."""
    return rol_requerido('aprendiz')(view_func)
