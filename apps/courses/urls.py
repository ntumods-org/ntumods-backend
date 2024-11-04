from django.urls import path

from apps.courses.views import (
    CourseListView,
    CourseDetailView,
    CourseIndexDetailView,
    CoursePrefixListView,
    CourseProgramListView,
    CoursePrerequisiteDetailView,
)


app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('code/<str:code>/', CourseDetailView.as_view(), name='course-detail'),
    path('index/<str:index>/', CourseIndexDetailView.as_view(), name='course-index-detail'),
    path('prefixes/', CoursePrefixListView.as_view(), name='course-prefix-list'),
    path('programs/', CourseProgramListView.as_view(), name='course-program-list'),
    path('course-prerequisite/<str:code>/', CoursePrerequisiteDetailView.as_view(), name='course-prerequisite-detail'),
]
