from django.urls import path

from . import views


app_name = 'scraper'

urlpatterns = [
    path('course/', views.get_course_data, name='scraper-course'),
    path('exam/', views.get_exam_data, name='scraper-exam'),
]
