from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.common.permissions import IsSuperUser
from apps.courses.models import Course
from apps.scraper.decorators import custom_swagger_index_schema
from apps.scraper.utils.course_scraper import perform_course_scraping
from apps.scraper.utils.detail_scraper import perform_course_detail_scraping
from apps.scraper.utils.exam_scraper import perform_exam_schedule_scraping
from apps.scraper.utils.program_scraper import perform_program_scraping


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_course_data(_):
    perform_course_scraping()
    return Response('Course Scraping Completed!')

@custom_swagger_index_schema
@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_detail_data(request):
    start_index = request.query_params.get('start_index', 0)
    end_index = request.query_params.get('end_index', Course.objects.count())
    perform_course_detail_scraping(int(start_index), int(end_index))
    return Response('Course Detail Scraping Completed!')

@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_exam_data(_):
    perform_exam_schedule_scraping()
    return Response('Exam Scraping Completed!')

@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_program_data(_):
    perform_program_scraping()
    return Response('Program Scraping Completed!')
