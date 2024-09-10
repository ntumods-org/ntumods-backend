from django.urls import path
from django.http import HttpResponse


app_name = 'optimizer'

urlpatterns = [
    path('', lambda request: HttpResponse('Hello, world!'), name='index'),
]
