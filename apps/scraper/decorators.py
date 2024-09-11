from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def custom_swagger_index_schema(func):
    return swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('start_index', openapi.IN_QUERY, description="Start index for scraping (inclusive)", type=openapi.TYPE_INTEGER, default=0),
            openapi.Parameter('end_index', openapi.IN_QUERY, description="End index for scraping (exclusive)", type=openapi.TYPE_INTEGER, default=None)
        ]
    )(func)
