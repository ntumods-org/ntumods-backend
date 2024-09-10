from django.db.models import Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.courses.models import Course


'''
Custom pagination class to be used in GenericAPIView classes.
- page_size_query_param: Allows the client to specify the number of items per page, default is 10.
- get_page_number: Allows the client to specify the page number, default is 1.
If client specifies a page number greater than the total number of pages, the last page is returned.
- get_paginated_response: Returns a custom response with the total number of items,
    the previous and next page links, the total number of pages, and the results.
'''
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    
    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param, 1)
        return min(int(page_number), paginator.num_pages)

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'prev': self.get_previous_link(),
            'next': self.get_next_link(),
            'total_pages': self.page.paginator.num_pages,
            'results': data,
        })


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
Custom mixin class to be used in CourseListView.
Applied various query parameters for filtering, ordering, and searching.
Applied custom pagination class.
'''
class CourseQueryParamsMixin:
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        CustomCodeAndNameSearch,
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
