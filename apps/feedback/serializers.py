from rest_framework import serializers

from apps.feedback.models import FeedbackForm


class FeedbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = [
            'id',
            'contact',
            'type',
            'title',
            'details',
        ]
