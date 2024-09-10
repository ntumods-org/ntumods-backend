from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.courses.models import Course, CourseIndex
from apps.courses.serializers import (
    CoursePartialSerializer,
    CourseIndexSerializer,
    CourseCompleteSerializer,
)


class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursePartialSerializer

class CourseDetailView(RetrieveAPIView):
    lookup_field = 'code'
    serializer_class = CourseCompleteSerializer

    def get_object(self):
        return get_object_or_404(Course, code=self.kwargs['code'])

class CourseIndexDetailView(RetrieveAPIView):
    lookup_field = 'index'
    serializer_class = CourseIndexSerializer

    def get_object(self):
        return get_object_or_404(CourseIndex, index=self.kwargs['index'])
