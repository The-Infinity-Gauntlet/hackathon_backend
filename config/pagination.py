from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPageNumberPagination(PageNumberPagination):
    """Default pagination for the API.

    - Supports `?page=` and `?page_size=` query params
    - Caps page_size to 100
    - Echoes the `ordering` parameter (when present) in the response
    """

    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        ordering = None
        try:
            ordering = self.request.query_params.get("ordering")
        except Exception:
            ordering = None

        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "ordering": ordering,
                "results": data,
            }
        )
