from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets

from .filters import BookingInfoFilter
from .models import BookingInfo, BookingReservation
from .serializers import BookingInfoSerializer, BookingReservationSerializer


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


class BookingReservationViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    create:
        Creates a :model:`listings.BookingReservation` object.

    retrieve:
        Retrieves a :model:`listings.BookingReservation` instance.

    list:
        Returns a list of :model:`listings.BookingReservation` objects.

    """

    queryset = BookingReservation.objects.all()
    serializer_class = BookingReservationSerializer
