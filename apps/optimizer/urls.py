from django.urls import path

from .views import OptimizeView


app_name = 'optimizer'

urlpatterns = [
    path('optimize/', OptimizeView.as_view(), name='optimize'),
]
