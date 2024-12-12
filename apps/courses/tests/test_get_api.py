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
        self.assertEqual(resp.data['count'], 20)
        self.assertEqual(resp.data['total_pages'], 2)
        
    def test_search_icontains_1(self):
        resp = self.client_anonymous.get(self.ENDPOINT, {'search__icontains': 'math'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 3)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1300')
        self.assertEqual(resp.data['results'][0]['name'], 'FOUNDATIONS OF MATHEMATICS')
        self.assertEqual(resp.data['results'][1]['code'], 'MH1810')
        self.assertEqual(resp.data['results'][1]['name'], 'MATHEMATICS 1')
        self.assertEqual(resp.data['results'][2]['code'], 'MH1811')
        self.assertEqual(resp.data['results'][2]['name'], 'MATHEMATICS 2')
        
    def test_search_icontains_2(self):
        resp = self.client_anonymous.get(self.ENDPOINT, {'search__icontains': 'MH1201 lin'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1200')
        self.assertEqual(resp.data['results'][0]['name'], 'LINEAR ALGEBRA I')


class CourseIndexDetailAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = (lambda _, course_index: reverse('courses:course-index-detail', kwargs={'index': course_index}))
    
    def test_fail_not_found(self):
        resp = self.client_anonymous.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client_anonymous.get(self.ENDPOINT('70181'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['index'], '70181')


class CourseDetailAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = (lambda _, course_code: reverse('courses:course-detail', kwargs={'code': course_code}))
    
    def test_fail_not_found(self):
        resp = self.client_anonymous.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client_anonymous.get(self.ENDPOINT('MH1100'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['code'], 'MH1100')
        self.assertEqual(resp.data['name'], 'CALCULUS I')


class CoursePrerequisiteAPITestCase(BaseAPITestCase):
    fixtures = ['sample_data.json']
    ENDPOINT = (lambda _, course_code: reverse('courses:course-prerequisite-detail', kwargs={'code': course_code}))
    
    def test_fail_not_found(self):
        resp = self.client_anonymous.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)

    def test_prerequisite_1(self):
        # MH1811 Prerequisite: MH1810 applicable to AY2017 cohorts onwards
        resp = self.client_anonymous.get(self.ENDPOINT('MH1811'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['child_nodes'], 'MH1810')
    
    def test_prerequisite_2(self):
        # SC2207 Prerequisite: SC2006(Corequisite) OR SC1007
        resp = self.client_anonymous.get(self.ENDPOINT('SC2207'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['child_nodes'], {
            "or": [
                {
                    "corequisite": "SC2006"
                },
                "SC1007"
            ]
        })

    def test_prerequisite_3(self):
        # MH4311 Prerequisite: (MH1200 OR MH1811) & (MH1100 OR MH1810) & MH1300
        resp = self.client_anonymous.get(self.ENDPOINT('MH4311'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['child_nodes'], {
            "and": [
                { 
                    "or": [
                        "MH1200",
                        "MH1811"
                    ]
                },
                { 
                    "or": [
                        "MH1100",
                        "MH1810"
                    ]
                },
                "MH1300"
            ]
        })

    def test_prerequisite_4(self):
        # MH4320 Prerequisite: (MH1200 & MH1811) OR (MH1100 & (MH1810 & MH1300))
        resp = self.client_anonymous.get(self.ENDPOINT('MH4320'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['child_nodes'], {
            "or": [
                { 
                    "and": [
                        "MH1200",
                        "MH1811"
                    ]
                },
                { 
                    "and": [
                        "MH1100",
                        { 
                            "and": [
                                "MH1810",
                                "MH1300"
                            ]
                        }
                    ]
                }
            ]
        })
