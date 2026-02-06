from django.urls import path
from .views import ProyectoViewSet

proyecto_list = ProyectoViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
proyecto_detail = ProyectoViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', proyecto_list, name='proyecto_list_create'),
    path('<int:pk>/', proyecto_detail, name='proyecto_detail_update_delete'),
]
