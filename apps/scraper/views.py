from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.common.permissions import IsSuperUser
from apps.scraper.utils.course_scraper import perform_course_scraping


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_course_data(_):
    perform_course_scraping()
    return Response('Course Scraping Completed!')
