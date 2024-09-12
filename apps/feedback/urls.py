from django.urls import path

from .views import FeedbackCreateView


app_name = 'feedback'

urlpatterns = [
    path('', FeedbackCreateView.as_view(), name='feedback-create'),
]
