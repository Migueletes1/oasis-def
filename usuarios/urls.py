from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_empresa_view, name='registro_empresa'),
    path('registro/pendiente/', views.registro_pendiente_view, name='registro_pendiente'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Admin AJAX endpoints
    path('admin/aprobar-empresa/<int:pk>/', views.admin_aprobar_empresa, name='admin_aprobar_empresa'),
    path('admin/rechazar-empresa/<int:pk>/', views.admin_rechazar_empresa, name='admin_rechazar_empresa'),
    path('admin/toggle-destacado/<int:pk>/', views.admin_toggle_destacado, name='admin_toggle_destacado'),

    # Admin CRUD — Proyectos
    path('admin/proyecto/nuevo/', views.admin_proyecto_form, name='admin_proyecto_nuevo'),
    path('admin/proyecto/<int:pk>/editar/', views.admin_proyecto_form, name='admin_proyecto_editar'),
    path('admin/proyecto/<int:pk>/eliminar/', views.admin_proyecto_delete, name='admin_proyecto_eliminar'),
    path('admin/api/buscar-aprendiz/', views.admin_buscar_aprendiz, name='admin_buscar_aprendiz'),

    # Admin CRUD — Carreras
    path('admin/carreras/', views.admin_carreras_list, name='admin_carreras_list'),
    path('admin/carrera/nueva/', views.admin_carrera_form, name='admin_carrera_nueva'),
    path('admin/carrera/<int:pk>/editar/', views.admin_carrera_form, name='admin_carrera_editar'),
    path('admin/carrera/<int:pk>/eliminar/', views.admin_carrera_delete, name='admin_carrera_eliminar'),

    # Admin — Empresa detalle
    path('admin/empresa/<int:pk>/detalle/', views.admin_empresa_detalle, name='admin_empresa_detalle'),

    # Backup endpoints
    path('admin/backup/create/', views.admin_backup_create, name='admin_backup_create'),
    path('admin/backup/download/<int:pk>/', views.admin_backup_download, name='admin_backup_download'),
    path('admin/backup/delete/<int:pk>/', views.admin_backup_delete, name='admin_backup_delete'),
    path('admin/backup/restore/<int:pk>/', views.admin_backup_restore, name='admin_backup_restore'),
    path('admin/backup/verify/<int:pk>/', views.admin_backup_verify, name='admin_backup_verify'),
]
