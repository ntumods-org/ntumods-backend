from django.urls import path

from .views import FeedbackView


app_name = 'feedback'

urlpatterns = [
    path('', FeedbackView.as_view(), name='feedback'),
]
