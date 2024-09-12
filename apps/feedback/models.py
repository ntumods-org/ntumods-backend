from django.db import models
from django.utils import timezone as tz


class FeedbackForm(models.Model):
    '''
    FeedbackForm model to store feedbacks from users. Fields include:
    - contact: optional contact information (email / telegram / etc.) for follow-up
    - type: type of feedback (bug report, feature request, etc.)
    - title: title of the feedback
    - details: details of the feedback
    '''
    class Type(models.TextChoices):
        BUG_REPORT = 'Bug Report', 'Bug Report'
        FEATURE_REQUEST = 'Feature Request', 'Feature Request'
        IMPROVEMENT_SUGGESTION = 'Improvement Suggestion', 'Improvement Suggestion'
        REQUEST_ASSISTANCE = 'Request Assistance', 'Request Assistance'
        OTHERS = 'Others', 'Others'

    contact = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=100)
    details = models.TextField()

    '''
    Fields for internal use only:
    - creation_time: time of creation of the feedback
    - acknowledged: changes to True when feedback is acknowledged
    - resolved: changes to True when feedback is resolved
    - internal_notes: any notes for internal use
    '''
    creation_time = models.DateTimeField(default=tz.now)
    acknowledged = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Feedback Forms'

    def __str__(self):
        return f'<Feedback #{self.id}: ({self.type}) {self.title}>'
