from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.scraper.utils.course_scraper import perform_course_scraping


@api_view(['GET'])
def index(request):
    perform_course_scraping()
    return Response({'message': 'Course scraping has been performed successfully!'})
