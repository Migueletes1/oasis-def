from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """
    Custom User Model con RBAC para OASIS.
    Roles: aprendiz, instructor, empresa, admin.
    """

    class Rol(models.TextChoices):
        APRENDIZ = 'aprendiz', 'Aprendiz'
        INSTRUCTOR = 'instructor', 'Instructor'
        EMPRESA = 'empresa', 'Empresa'
        ADMIN = 'admin', 'Administrador'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.APRENDIZ,
        db_index=True,
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?\d{7,15}$',
            message='Ingrese un numero de telefono valido (7-15 digitos).',
        )],
    )
    avatar_url = models.URLField(blank=True)

    # Campos especificos para empresa
    nombre_empresa = models.CharField(max_length=200, blank=True)
    nit_empresa = models.CharField(max_length=20, blank=True, unique=True, null=True)
    motivo_registro = models.TextField(
        blank=True,
        help_text='Motivo de registro (requerido para empresas).',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        if self.rol == self.Rol.EMPRESA and self.nombre_empresa:
            return f"{self.nombre_empresa} ({self.email})"
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_empresa(self):
        return self.rol == self.Rol.EMPRESA

    @property
    def es_instructor(self):
        return self.rol == self.Rol.INSTRUCTOR

    @property
    def es_aprendiz(self):
        return self.rol == self.Rol.APRENDIZ

    @property
    def iniciales(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()

    @property
    def esta_pendiente(self):
        return self.es_empresa and not self.is_active
