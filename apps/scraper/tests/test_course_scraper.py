from rest_framework.test import APITestCase
import os

from apps.courses.models import Course, CourseIndex
from apps.scraper.utils.course_scraper import get_raw_data, process_data, save_course_data
from apps.scraper.utils.exam_scraper import get_soup_from_html_file


class TestCourseScraper(APITestCase):
    '''
    Given soup of courses page, test these functions from `test_course_scraper`:
    - get_raw_data
    - process_data
    - save_course_data
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FILE_PATH = os.path.join('apps', 'scraper', 'utils', 'scraping_files', 'course_schedule.html')
        self.soup = get_soup_from_html_file(FILE_PATH)

    def get_schedule_str(self, *args):
        # return a string of 'O' of length 192 (32 * 6) with 'X' on the given args (1 index)
        schedule_list = ['O'] * 192
        for arg in args:
            schedule_list[arg - 1] = 'X'
        return ''.join(schedule_list)

    def test_course_scraper_1(self):
        raw_data = get_raw_data(self.soup, 0, 0)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AAA08B",
                    "course_name": "FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN",
                    "academic_units": 3,
                },
                [
                    {
                        "index": "39619",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LE",
                                "day": "THU",
                                "time": "1330-1620",
                                "venue": "NIE7-02-07",
                                "remark": "",
                            }
                        ],
                    }
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAA08B",
                "course_name": "FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN",
                "academic_units": 3,
                "prefix": "AAA",
                "level": 10,
                "indexes": [
                    {
                        "index": "39619",
                        "schedule": self.get_schedule_str(108, 109, 110, 111, 112, 113),
                        "information": "LEC/STUDIO^LE^THU^1330-1620^NIE7-02-07^",
                        "filtered_information": "",
                    }
                ],
                "common_schedule": self.get_schedule_str(108, 109, 110, 111, 112, 113),
                "common_information": "LEC/STUDIO^LE^THU^1330-1620^NIE7-02-07^",
            }
        ])
        save_course_data(processed_data)
        course_code = Course.objects.get(code='AAA08B')
        self.assertEqual(course_code.name, 'FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str(108, 109, 110, 111, 112, 113))
        course_index = CourseIndex.objects.get(index='39619')
        self.assertEqual(course_index.course, course_code)
        self.assertEqual(course_index.schedule, self.get_schedule_str(108, 109, 110, 111, 112, 113))
        self.assertEqual(course_index.information, "LEC/STUDIO^LE^THU^1330-1620^NIE7-02-07^")
        self.assertEqual(course_index.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LE",
                "day": "THU",
                "time": "1330-1620",
                "venue": "NIE7-02-07",
                "remark": "",
            }

        ])

    def test_course_scraper_2(self):
        raw_data = get_raw_data(self.soup, 4, 4)
        self.assertEqual(raw_data,
        [
            (

                {
                    "course_code": "AAA18E",
                    "course_name": "DRAWING",
                    "academic_units": 3
                },
                [
                    {
                        "index": "39621",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG1",
                                "day": "TUE",
                                "time": "1130-1420",
                                "venue": "NIE3-B1-10",
                                "remark": "",
                            }
                        ],
                    },
                    {
                        "index": "39622",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG2",
                                "day": "WED",
                                "time": "1130-1420",
                                "venue": "NIE-TR319",
                                "remark": "Teaching Wk1-11,13",
                            }
                        ],
                    },
                    {
                        "index": "39623",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG3",
                                "day": "WED",
                                "time": "1430-1720",
                                "venue": "NIE-TR319",
                                "remark": "Teaching Wk1-11,13",
                            }
                        ],
                    },
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAA18E",
                "course_name": "DRAWING",
                "academic_units": 3,
                "prefix": "AAA",
                "level": 10,
                "indexes": [
                    {
                        "index": "39621",
                        "schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOXXXXXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                        "information": "LEC/STUDIO^LG1^TUE^1130-1420^NIE3-B1-10^",
                        "filtered_information": "LEC/STUDIO^LG1^TUE^1130-1420^NIE3-B1-10^"
                    },
                    {
                        "index": "39622",
                        "schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOXXXXXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                        "information": "LEC/STUDIO^LG2^WED^1130-1420^NIE-TR319^Teaching Wk1-11,13",
                        "filtered_information": "LEC/STUDIO^LG2^WED^1130-1420^NIE-TR319^Teaching Wk1-11,13"
                    },
                    {
                        "index": "39623",
                        "schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOXXXXXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                        "information": "LEC/STUDIO^LG3^WED^1430-1720^NIE-TR319^Teaching Wk1-11,13",
                        "filtered_information": "LEC/STUDIO^LG3^WED^1430-1720^NIE-TR319^Teaching Wk1-11,13"
                    },
                ],
                "common_schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                "common_information": "",
            }
        ])
        save_course_data(processed_data)
        course_code = Course.objects.get(code='AAA18E')
        self.assertEqual(course_code.name, 'DRAWING')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str())
        course_index_1 = CourseIndex.objects.get(index='39621')
        self.assertEqual(course_index_1.course, course_code)
        self.assertEqual(course_index_1.schedule, self.get_schedule_str(40, 41, 42, 43, 44, 45))
        self.assertEqual(course_index_1.information, "LEC/STUDIO^LG1^TUE^1130-1420^NIE3-B1-10^")
        self.assertEqual(course_index_1.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG1",
                "day": "TUE",
                "time": "1130-1420",
                "venue": "NIE3-B1-10",
                "remark": "",
            }
        ])
        course_index_2 = CourseIndex.objects.get(index='39622')
        self.assertEqual(course_index_2.course, course_code)
        self.assertEqual(course_index_2.schedule, self.get_schedule_str(72, 73, 74, 75, 76, 77))
        self.assertEqual(course_index_2.information, "LEC/STUDIO^LG2^WED^1130-1420^NIE-TR319^Teaching Wk1-11,13")
        self.assertEqual(course_index_2.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG2",
                "day": "WED",
                "time": "1130-1420",
                "venue": "NIE-TR319",
                "remark": "Teaching Wk1-11,13",
            }
        ])
        course_index_3 = CourseIndex.objects.get(index='39623')
        self.assertEqual(course_index_3.course, course_code)
        self.assertEqual(course_index_3.schedule, self.get_schedule_str(78, 79, 80, 81, 82, 83))
        self.assertEqual(course_index_3.information, "LEC/STUDIO^LG3^WED^1430-1720^NIE-TR319^Teaching Wk1-11,13")
        self.assertEqual(course_index_3.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG3",
                "day": "WED",
                "time": "1430-1720",
                "venue": "NIE-TR319",
                "remark": "Teaching Wk1-11,13",
            }
        ])

    def test_course_scraper_3(self):
        raw_data = get_raw_data(self.soup, 17, 17)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AAE18B",
                    "course_name": "LANGUAGE IN CONTEXT",
                    "academic_units": 3,
                },
                [
                    {
                        "index": "39291",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LE",
                                "day": "THU",
                                "time": "1130-1220",
                                "venue": "NIE3-TR318",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "T",
                                "day": "WED",
                                "time": "1430-1620",
                                "venue": "NIE3-TR318",
                                "remark": "",
                            },
                        ],
                    }
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAE18B",
                "course_name": "LANGUAGE IN CONTEXT",
                "academic_units": 3,
                "prefix": "AAE",
                "level": 10,
                "indexes": [
                    {
                        "index": "39291",
                        "schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOXXXXOOOOOOOOOOOOOOOOOOOOOOXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                        "information": "LEC/STUDIO^LE^THU^1130-1220^NIE3-TR318^;TUT^T^WED^1430-1620^NIE3-TR318^",
                        "filtered_information": "",
                    }
                ],
                "common_schedule": "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOXXXXOOOOOOOOOOOOOOOOOOOOOOXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
                "common_information": "LEC/STUDIO^LE^THU^1130-1220^NIE3-TR318^;TUT^T^WED^1430-1620^NIE3-TR318^",
            }
        ])
        save_course_data(processed_data)
        course_code = Course.objects.get(code='AAE18B')
        self.assertEqual(course_code.name, 'LANGUAGE IN CONTEXT')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str(78, 79, 80, 81, 104, 105))
        course_index = CourseIndex.objects.get(index='39291')
        self.assertEqual(course_index.course, course_code)
        self.assertEqual(course_index.schedule, self.get_schedule_str(78, 79, 80, 81, 104, 105))
        self.assertEqual(course_index.information, "LEC/STUDIO^LE^THU^1130-1220^NIE3-TR318^;TUT^T^WED^1430-1620^NIE3-TR318^")
        self.assertEqual(course_index.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LE",
                "day": "THU",
                "time": "1130-1220",
                "venue": "NIE3-TR318",
                "remark": "",
            },
            {
                "type": "TUT",
                "group": "T",
                "day": "WED",
                "time": "1430-1620",
                "venue": "NIE3-TR318",
                "remark": "",
            },
        ])
