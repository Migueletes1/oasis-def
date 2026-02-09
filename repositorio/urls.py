from django.urls import path
from . import views

app_name = 'repositorio'

urlpatterns = [
    path('', views.explorador, name='explorador'),
    path('proyecto/<int:pk>/', views.proyecto_detalle, name='detalle'),
    path('proyecto/<int:pk>/votar/', views.votar_proyecto, name='votar'),
    path('descargar/<int:archivo_id>/', views.descargar_archivo, name='descargar'),
    path('proyecto/<int:pk>/subir/', views.subir_archivos, name='subir_archivos'),
]
