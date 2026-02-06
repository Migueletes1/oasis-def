from django.urls import path
from .views import EmpresaViewSet

empresa_list = EmpresaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
empresa_detail = EmpresaViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', empresa_list, name='empresa_list_create'),
    path('<int:pk>/', empresa_detail, name='empresa_detail_update_delete'),
]
