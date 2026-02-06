from django.urls import path
from .views import EvaluacionViewSet

evaluacion_list = EvaluacionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
evaluacion_detail = EvaluacionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', evaluacion_list, name='evaluacion_list_create'),
    path('<int:pk>/', evaluacion_detail, name='evaluacion_detail_update_delete'),
]
