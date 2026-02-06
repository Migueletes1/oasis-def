from django.urls import path
from .views import SeguimientoViewSet

seguimiento_list = SeguimientoViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
seguimiento_detail = SeguimientoViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', seguimiento_list, name='seguimiento_list_create'),
    path('<int:pk>/', seguimiento_detail, name='seguimiento_detail_update_delete'),
]
