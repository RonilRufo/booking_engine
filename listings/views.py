from django_filters import rest_framework as filters
from rest_framework import viewsets

from .filters import BookingInfoFilter
from .models import BookingInfo
from .serializers import BookingInfoSerializer


class BookingInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
        Retrieves a :model:`listings.BookingInfo` instance.

    list:
        Returns a list of :model:`listings.BookingInfo` objects.

    """

    queryset = BookingInfo.objects.order_by("price")
    serializer_class = BookingInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookingInfoFilter
