from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.superuser = User.objects.create_superuser('admin')
        self.client_anonymous = APIClient()
        self.client_superuser = APIClient()
        self.client_superuser.force_authenticate(user=self.superuser)


class CourseListAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = reverse('courses:course-list')
    
    def test_get_success(self):
        resp = self.client_anonymous.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 12)
        self.assertEqual(resp.data['total_pages'], 2)
        
    def test_search_icontains_1(self):
        resp = self.client_anonymous.get(self.ENDPOINT, {'search__icontains': 'math'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 5)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1301')
        self.assertEqual(resp.data['results'][0]['name'], 'DISCRETE MATHEMATICS')
        self.assertEqual(resp.data['results'][1]['code'], 'MH1801')
        self.assertEqual(resp.data['results'][1]['name'], 'MATHEMATICS 1')
        self.assertEqual(resp.data['results'][2]['code'], 'MH1811')
        self.assertEqual(resp.data['results'][2]['name'], 'MATHEMATICS 2')
        self.assertEqual(resp.data['results'][3]['code'], 'MH1812')
        self.assertEqual(resp.data['results'][3]['name'], 'DISCRETE MATHEMATICS')
        self.assertEqual(resp.data['results'][4]['code'], 'MH2811')
        self.assertEqual(resp.data['results'][4]['name'], 'MATHEMATICS II')
        
    def test_search_icontains_1(self):
        resp = self.client_anonymous.get(self.ENDPOINT, {'search__icontains': 'MH1201 lin'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1201')
        self.assertEqual(resp.data['results'][0]['name'], 'LINEAR ALGEBRA II')


class CourseIndexDetailAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = (lambda _, course_index: reverse('courses:course-index-detail', kwargs={'index': course_index}))
    
    def test_fail_not_found(self):
        resp = self.client_anonymous.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client_anonymous.get(self.ENDPOINT('70501'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['index'], '70501')


class CourseDetailAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = (lambda _, course_code: reverse('courses:course-detail', kwargs={'code': course_code}))
    
    def test_fail_not_found(self):
        resp = self.client_anonymous.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client_anonymous.get(self.ENDPOINT('MH1101'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['code'], 'MH1101')
        self.assertEqual(resp.data['name'], 'CALCULUS II')
