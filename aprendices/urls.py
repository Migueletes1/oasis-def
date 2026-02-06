from django.urls import path
from .views import AprendizViewSet

aprendiz_list = AprendizViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
aprendiz_detail = AprendizViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', aprendiz_list, name='aprendiz_list_create'),
    path('<int:pk>/', aprendiz_detail, name='aprendiz_detail_update_delete'),
]
