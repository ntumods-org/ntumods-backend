from django.urls import path

from apps.optimizer.views import OptimizeView, GenScheduleView


app_name = 'optimizer'

urlpatterns = [
    path('optimize/', OptimizeView.as_view(), name='optimize'),
    path('generate-schedule/', GenScheduleView.as_view(), name='generate-schedule'),
]
