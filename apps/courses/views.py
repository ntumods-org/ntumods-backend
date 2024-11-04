from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response

from apps.courses.mixins import CourseQueryParamsMixin
from apps.courses.models import Course, CourseIndex, CoursePrefix, CoursePrerequisite, CourseProgram
from apps.courses.serializers import (
    CoursePartialSerializer,
    CourseIndexSerializer,
    CourseCompleteSerializer,
    CourseProgramSerializer,
    CoursePrerequisiteSerializer,
)
from apps.courses.utils import getPrerequisites


class CourseListView(CourseQueryParamsMixin, generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursePartialSerializer


class CourseDetailView(generics.RetrieveAPIView):
    lookup_field = 'code'
    serializer_class = CourseCompleteSerializer

    def get_object(self):
        return get_object_or_404(Course, code=self.kwargs['code'])


class CourseIndexDetailView(generics.RetrieveAPIView):
    lookup_field = 'index'
    serializer_class = CourseIndexSerializer

    def get_object(self):
        return get_object_or_404(CourseIndex, index=self.kwargs['index'])


class CoursePrefixListView(generics.GenericAPIView):
    def get(self, request):
        programs = CoursePrefix.objects.values_list('prefix', flat=True)
        return Response(programs)


class CourseProgramListView(generics.ListAPIView):
    serializer_class = CourseProgramSerializer
    queryset = CourseProgram.objects.all()


class CoursePrerequisiteDetailView(generics.RetrieveAPIView):
    lookup_field = 'course'
    serializer_class = CoursePrerequisiteSerializer

    def get_object(self):
        # Populate CoursePrerequisite table if empty
        if len(CoursePrerequisite.objects.all()) == 0:
            print("Populating CoursePrerequisite table...")
            getPrerequisites()
            print("Completed.")
        course = Course.objects.get(code=self.kwargs['code'])
        return get_object_or_404(CoursePrerequisite, course=course)
