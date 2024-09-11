from rest_framework.test import APITestCase
import os

from apps.courses.models import Course
from apps.scraper.utils.exam_scraper import get_soup_from_html_file, get_raw_data, process_data, save_exam_schedule


class TestExamScraper(APITestCase):
    '''
    Given soup of exam schedule page, test these functions from `test_exam_scraper`:
    - get_raw_data
    - process_data
    - save_exam_schedule
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FILE_PATH = os.path.join('apps', 'scraper', 'utils', 'scraping_files', 'exam_schedule_test.html')
        self.soup = get_soup_from_html_file(FILE_PATH)

    def get_exam_schedule_str(self, date_str, time_str, *args):
        schedule_list = ['O'] * 32
        for arg in args:
            schedule_list[arg - 1] = 'X'
        return date_str + time_str + ''.join(schedule_list)

    def create_course_code(self, code):
        return Course.objects.create(code=code, name='sample', academic_units=4, common_schedule='O' * 192)

    def test_exam_scraper_1(self):
        raw_data = get_raw_data(self.soup)[:3] # test only first 3 rows
        self.assertEqual(raw_data, [
            {
                "date": "26 April 2024",
                "day": "Friday",
                "time": "9.00 am",
                "course_code": "AC2101",
                "course_title": "ACCOUNTING RECOGNITION & MEASUREMENT",
                "duration": "2 hr 30 min",
            },
            {
                "date": "26 April 2024",
                "day": "Friday",
                "time": "9.00 am",
                "course_code": "BA3203",
                "course_title": "ACTUARIAL ASPECTS OF ASSET VALUATION",
                "duration": "3 hr",
            },
            {
                "date": "26 April 2024",
                "day": "Friday",
                "time": "9.00 am",
                "course_code": "BF3204",
                "course_title": "FINANCIAL MODELLING",
                "duration": "2 hr",
            },
        ])
        data = process_data(raw_data)
        self.assertEqual(data, [
            {
                "course_code": "AC2101",
                "exam_schedule_str": "2024-04-2609:00-11:30OOXXXXXOOOOOOOOOOOOOOOOOOOOOOOOO",
            },
            {
                "course_code": "BA3203",
                "exam_schedule_str": "2024-04-2609:00-12:00OOXXXXXXOOOOOOOOOOOOOOOOOOOOOOOO",
            },
            {
                "course_code": "BF3204",
                "exam_schedule_str": "2024-04-2609:00-11:00OOXXXXOOOOOOOOOOOOOOOOOOOOOOOOOO",
            },
        ])
        self.create_course_code('AC2101')
        self.create_course_code('BA3203')
        self.create_course_code('BF3204')
        save_exam_schedule(data)
        course_1 = Course.objects.get(code='AC2101')
        self.assertEqual(
            course_1.exam_schedule,
            self.get_exam_schedule_str('2024-04-26', '09:00-11:30', 3, 4, 5, 6, 7))
        self.assertEqual(
            course_1.get_exam_schedule,
            {
                'date': '2024-04-26',
                'time': '09:00-11:30',
                'timecode': self.get_exam_schedule_str('', '', 3, 4, 5, 6, 7)
            })
        course_2 = Course.objects.get(code='BA3203')
        self.assertEqual(
            course_2.exam_schedule,
            self.get_exam_schedule_str('2024-04-26', '09:00-12:00', 3, 4, 5, 6, 7, 8))
        self.assertEqual(
            course_2.get_exam_schedule,
            {
                'date': '2024-04-26',
                'time': '09:00-12:00',
                'timecode': self.get_exam_schedule_str('', '', 3, 4, 5, 6, 7, 8)
            })
        course_3 = Course.objects.get(code='BF3204')
        self.assertEqual(
            course_3.exam_schedule,
            self.get_exam_schedule_str('2024-04-26', '09:00-11:00', 3, 4, 5, 6))
        self.assertEqual(
            course_3.get_exam_schedule,
            {
                'date': '2024-04-26',
                'time': '09:00-11:00',
                'timecode': self.get_exam_schedule_str('', '', 3, 4, 5, 6)
            })

    def test_exam_scraper_2(self):
        raw_data = get_raw_data(self.soup)[-2:] # test last 2 rows
        self.assertEqual(raw_data, [
            {
                "date": "9 May 2024",
                "day": "Thursday",
                "time": "1.00 pm",
                "course_code": "PH4608",
                "course_title": "PLASMONICS & METAMATERIALS",
                "duration": "2 hr 30 min",
            },
            {
                "date": "9 May 2024",
                "day": "Thursday",
                "time": "1.00 pm",
                "course_code": "SU2001",
                "course_title": "URBAN PLANNING & DESIGN",
                "duration": "2 hr",
            },
        ])
        data = process_data(raw_data)
        self.assertEqual(data, [
            {
                "course_code": "PH4608",
                "exam_schedule_str": "2024-05-0913:00-15:30OOOOOOOOOOXXXXXOOOOOOOOOOOOOOOOO",
            },
            {
                "course_code": "SU2001",
                "exam_schedule_str": "2024-05-0913:00-15:00OOOOOOOOOOXXXXOOOOOOOOOOOOOOOOOO",
            },
        ])
        self.create_course_code('PH4608')
        self.create_course_code('SU2001')
        save_exam_schedule(data)
        course_1 = Course.objects.get(code='PH4608')
        self.assertEqual(
            course_1.exam_schedule,
            self.get_exam_schedule_str('2024-05-09', '13:00-15:30', 11, 12, 13, 14, 15))
        self.assertEqual(
            course_1.get_exam_schedule,
            {
                'date': '2024-05-09',
                'time': '13:00-15:30',
                'timecode': self.get_exam_schedule_str('', '', 11, 12, 13, 14, 15)
            })
        course_2 = Course.objects.get(code='SU2001')
        self.assertEqual(
            course_2.exam_schedule,
            self.get_exam_schedule_str('2024-05-09', '13:00-15:00', 11, 12, 13, 14))
        self.assertEqual(
            course_2.get_exam_schedule,
            {
                'date': '2024-05-09',
                'time': '13:00-15:00',
                'timecode': self.get_exam_schedule_str('', '', 11, 12, 13, 14)
            })
