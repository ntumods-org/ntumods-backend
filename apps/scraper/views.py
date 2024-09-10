from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.common.permissions import IsSuperUser
from apps.scraper.utils.course_scraper import perform_course_scraping
from apps.scraper.utils.exam_scraper import perform_exam_schedule_scraping


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_course_data(_):
    perform_course_scraping()
    return Response('Course Scraping Completed!')

@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_exam_data(_):
    perform_exam_schedule_scraping()
    return Response('Exam Scraping Completed')
