from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


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
