from django.urls import path
from .views import InstructorViewSet

instructor_list = InstructorViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
instructor_detail = InstructorViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', instructor_list, name='instructor_list_create'),
    path('<int:pk>/', instructor_detail, name='instructor_detail_update_delete'),
]
