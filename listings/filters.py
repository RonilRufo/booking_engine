import datetime
from typing import List, Union

from django.db.models import Count, F, Q, QuerySet
from django_filters import rest_framework as filters

from .models import BookingInfo


class BookingInfoFilter(filters.FilterSet):
    """
    Custom filterset class for :model:`listings.BookingInfo`
    """

    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    check_in = filters.DateFilter(method="filter_check_in")
    check_out = filters.DateFilter(method="filter_check_out")

    class Meta:
        model = BookingInfo
        fields = (
            "max_price",
            "check_in",
            "check_out",
        )

    def check_in_and_check_out_filters(
        self, queryset: Union[QuerySet, List[BookingInfo]], value: datetime.date
    ) -> Union[QuerySet, List[BookingInfo]]:
        """
        Handles the filtering of check in and checkout dates for bookings.
        """
        return queryset.annotate(
            reservations_made=Count(
                "reservations",
                filter=Q(reservations__start_date__gte=value)
                | Q(reservations__end_date__lte=value),
            ),
            total_rooms=Count("hotel_room_type__hotel_rooms"),
            available_rooms=F("total_rooms") - F("reservations_made"),
        ).filter(available_rooms__gt=0)

    def filter_check_in(self, queryset, name, value):
        """
        Filters all listings that are available for the specified check in date.
        """
        if value is not None:
            queryset = self.check_in_and_check_out_filters(queryset, value)

        return queryset

    def filter_check_out(self, queryset, name, value):
        """
        Filters all listings that are available for the specified check out date.
        """
        if value is not None:
            queryset = self.check_in_and_check_out_filters(queryset, value)

        return queryset
