from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend, OrderingFilter

from apps.common.pagination import CustomPagination
from apps.courses.models import Course, CourseProgram


'''
Custom filter backend classes to be used in GenericAPIView classes.
Accepts query parameter `search__icontains`.
Search for courses whose code or name contains the search term, separated by spaces.
'''
class CustomCodeAndNameSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_qp = request.query_params.get('search__icontains', None)
        if search_qp:
            ret_queryset = Course.objects.none()
            for search_term in search_qp.split():
                ret_queryset |= queryset.filter(
                    code__icontains=search_term) | queryset.filter(name__icontains=search_term)
            return ret_queryset
        else:
            return queryset


'''
When query parameter `program__icontains` is provided, filter courses by program.
'''
class CustomProgramSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        program_qp = request.query_params.get('program__icontains', None)
        if not program_qp:
            return queryset
        programs_list = program_qp.split(';') if program_qp else None
        programs_list = [int(id.strip()) for id in programs_list if id.strip()]
        queryset = queryset.filter(programs__in=programs_list).distinct()
        return queryset


'''
When query parameter `year` is provided, filter courses by year.
'''
class CustomYearSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        year_qp = request.query_params.get('year', None)
        if not year_qp or year_qp not in ['1', '2', '3', '4', '5']:
            return queryset
        year_qp = int(year_qp)
        course_programs = CourseProgram.objects.filter(year=year_qp).values_list('id', flat=True)
        queryset = queryset.filter(programs__in=course_programs).distinct()
        return queryset


'''
When query parameter `level__in` is provided, filter courses by level.
Allows multiple levels separated by semicolons, e.g. `level__in=1;2;3`.
'''
class CustomLevelMultipleFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        level_qp = request.query_params.get('level__in', None)
        if not level_qp:
            return queryset
        levels = level_qp.split(';')
        return queryset.filter(level__in=levels)


'''
When query parameter `prefix` is provided, filter courses by program code.
Allows multiple program codes separated by semicolons, e.g. `prefix=ACC;MH;SC`.
'''
class PrefixMultipleFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        program_qp = request.query_params.get('prefix', None)
        print(program_qp)
        if not program_qp:
            return queryset
        programs = program_qp.split(';')
        return queryset.filter(prefix__in=programs)


'''
Custom mixin class to be used in CourseListView.
Applied various query parameters for filtering, ordering, and searching.
Applied custom pagination class.
'''
class CourseQueryParamsMixin:
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        CustomCodeAndNameSearch,
        CustomProgramSearch,
        CustomYearSearch,
        CustomLevelMultipleFilter,
        PrefixMultipleFilter,
    ]
    filterset_fields = {
        'code': ['icontains'],
        'name': ['icontains'],
        'academic_units': ['lte', 'gte'],
        'prerequisite': ['icontains'],
        'mutually_exclusive': ['icontains'],
        'not_available': ['icontains'],
        'not_available_all': ['icontains'],
        'offered_as_ue': ['exact'],
        'offered_as_bde': ['exact'],
        'grade_type': ['icontains'],
        'not_offered_as_core_to': ['icontains'],
        'not_offered_as_pe_to': ['icontains'],
        'not_offered_as_bde_ue_to': ['icontains'],
        'department_maintaining': ['icontains'],
        'program_list': ['icontains'],
    }
    ordering_fields = ['code', 'name', 'academic_units',]
    pagination_class = CustomPagination
