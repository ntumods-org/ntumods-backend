from rest_framework import generics

from apps.feedback.models import FeedbackForm
from apps.feedback.serializers import FeedbackFormSerializer


class FeedbackCreateView(generics.CreateAPIView):
    queryset = FeedbackForm.objects.all()
    serializer_class = FeedbackFormSerializer
