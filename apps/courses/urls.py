from django.urls import path
from apps.courses.views import (
    CourseListView,
    CourseDetailView,
    CourseIndexDetailView,
)


app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<str:code>/', CourseDetailView.as_view(), name='course-detail'),
    path('index/<str:index>/', CourseIndexDetailView.as_view(), name='course-index-detail'),
]
