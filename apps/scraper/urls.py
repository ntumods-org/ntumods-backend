from django.urls import path

from . import views


app_name = 'scraper'

urlpatterns = [
    path('course/', views.get_course_data, name='course'),
    path('detail/', views.get_detail_data, name='detail'),
    path('exam/', views.get_exam_data, name='exam'),
    path('program/', views.get_program_data, name='program'),
]
