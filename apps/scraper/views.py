from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.scraper.utils.course_scraper import perform_course_scraping
from apps.common.permissions import IsSuperUser


@api_view(['GET'])
@permission_classes([IsSuperUser])
def index(request):
    perform_course_scraping()
    return Response({'message': 'Course scraping has been performed successfully!'})
