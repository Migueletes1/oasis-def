from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'rol', 'nombre_empresa',
        'is_active', 'is_staff', 'date_joined',
    ]
    list_filter = ['rol', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'nombre_empresa', 'nit_empresa']
    list_editable = ['is_active', 'rol']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('OASIS - Rol y Datos', {
            'fields': ('rol', 'telefono', 'avatar_url'),
        }),
        ('Datos de Empresa', {
            'fields': ('nombre_empresa', 'nit_empresa', 'motivo_registro'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('OASIS - Rol', {
            'fields': ('rol', 'email'),
        }),
    )

    actions = ['aprobar_empresas', 'rechazar_empresas']

    @admin.action(description='Aprobar empresas seleccionadas')
    def aprobar_empresas(self, request, queryset):
        updated = queryset.filter(rol='empresa', is_active=False).update(is_active=True)
        self.message_user(request, f'{updated} empresa(s) aprobada(s) exitosamente.')

    @admin.action(description='Rechazar (desactivar) empresas seleccionadas')
    def rechazar_empresas(self, request, queryset):
        updated = queryset.filter(rol='empresa').update(is_active=False)
        self.message_user(request, f'{updated} empresa(s) desactivada(s).')
