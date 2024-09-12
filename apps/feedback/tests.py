from rest_framework.test import APITestCase

from apps.feedback.models import FeedbackForm


class FeedbackTestCase(APITestCase):
    def test_feedback_create_success(self):
        response = self.client.post('/feedback/', {
            'contact': '',
            'type': 'Feature Request',
            'title': 'Test Feature Request',
            'details': 'This is a test feature request.',

            # these fields below are not required and should not affect what's in the database
            'acknowledged': True,
            'resolved': True,
            'internal_notes': 'This is an internal note.'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['type'], 'Feature Request')
        feedback_instance = FeedbackForm.objects.get(id=response.data['id'])
        self.assertEqual(feedback_instance.title, 'Test Feature Request')
        self.assertEqual(feedback_instance.details, 'This is a test feature request.')
        self.assertEqual(feedback_instance.acknowledged, False)
        self.assertEqual(feedback_instance.resolved, False)
        self.assertEqual(feedback_instance.internal_notes, '')

    def test_feedback_create_fail_1(self):
        # title is a required field
        response = self.client.post('/feedback/', {
            'contact': '',
            'type': 'Feature Request',
            'details': 'This is a test feature request.',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['title'][0], 'This field is required.')

    def test_feedback_create_fail_2(self):
        # invalid type given
        response = self.client.post('/feedback/', {
            'contact': 'some contact info',
            'type': 'invalid type',
            'title': 'Test Feature Request',
            'details': 'This is a test feature request.'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['type'][0], '"invalid type" is not a valid choice.')

    def test_feedback_create_fail_3(self):
        # exceeding max length of contact
        response = self.client.post('/feedback/', {
            'contact': 'X' * 101,
            'type': 'Others',
            'title': 'Test Feature Request',
            'details': 'This is a test feature request.'
        })
        self.assertEqual(response.status_code, 400)
