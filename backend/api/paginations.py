from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGINATION_NUMBER


class CustomPagination(PageNumberPagination):
    page_size = PAGINATION_NUMBER
    page_size_query_param = "limit"
