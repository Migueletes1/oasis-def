from django.urls import path
from .views import AsignacionViewSet

asignacion_list = AsignacionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
asignacion_detail = AsignacionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', asignacion_list, name='asignacion_list_create'),
    path('<int:pk>/', asignacion_detail, name='asignacion_detail_update_delete'),
]
