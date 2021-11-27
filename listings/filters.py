import datetime
from typing import List, Union

from django.db.models import Case, Count, F, IntegerField, Q, QuerySet, Value, When
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import serializers

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

    def filter_check_in(self, queryset, name, value):
        """
        Unused in favor of `filter_check_in_and_check_out_bookings`.
        """
        return queryset

    def filter_check_out(self, queryset, name, value):
        """
        Unused in favor of `filter_check_in_and_check_out_bookings`.
        """
        return queryset

    def filter_check_in_and_check_out_bookings(
        self,
        queryset: Union[QuerySet, List[BookingInfo]],
        check_in: datetime.date,
        check_out: datetime.date,
    ) -> Union[QuerySet, List[BookingInfo]]:
        """
        Returns queryset based on whether rooms/apartments are available on a given
        check in / check out range.
        """
        return queryset.annotate(
            # Get all reservations that overlap the given check in and check out dates.
            reservations_made=Count(
                "reservations",
                filter=(
                    Q(
                        reservations__start_date__lte=check_in,
                        reservations__end_date__gte=check_in,
                    )
                    | Q(
                        reservations__start_date__lte=check_out,
                        reservations__end_date__gte=check_out,
                    )
                    | Q(
                        reservations__start_date__gte=check_in,
                        reservations__end_date__lte=check_out,
                    )
                    | Q(
                        reservations__start_date__lte=check_in,
                        reservations__end_date__gte=check_out,
                    )
                ),
                distinct=True,
            ),
            # Get the total rooms for each listing. Hotel rooms count for hotels while
            # apartments always return 1.
            total_rooms=Case(
                When(
                    listing__isnull=False,  # For apartment bookings
                    then=Value(1),
                ),
                When(
                    hotel_room_type__isnull=False,  # For hotel bookings
                    then=Count("hotel_room_type__hotel_rooms", distinct=True),
                ),
                default=Value(0),
                output_field=IntegerField(),
            ),
            available_rooms=F("total_rooms") - F("reservations_made"),
        ).filter(available_rooms__gt=0)

    def filter_queryset(self, queryset):
        """
        Executes the filtering in the queryset but with an additional validation for
        check_in and check_out fields.
        """
        if "check_in" in self.request.GET and "check_out" not in self.request.GET:
            raise serializers.ValidationError(_("Please provide check_out value."))

        if "check_out" in self.request.GET and "check_in" not in self.request.GET:
            raise serializers.ValidationError(_("Please provide check_in value."))

        # Validate check in and check out values. Check in date must not be later than
        # check out date.
        if "check_in" in self.request.GET and "check_out" in self.request.GET:
            check_in = datetime.datetime.strptime(
                self.request.GET.get("check_in"), "%Y-%m-%d"
            )
            check_out = datetime.datetime.strptime(
                self.request.GET.get("check_out"), "%Y-%m-%d"
            )

            if check_in > check_out:
                raise serializers.ValidationError(
                    _("Check in date must not be later than check out date.")
                )

            # NOTE: By default, filtering is done on each field separately. We can't do
            # that for check in and check out date range. We need both fields to
            # properly filter the reservations made. Hence, the implementation of this
            # custom filter method.
            queryset = self.filter_check_in_and_check_out_bookings(
                queryset,
                check_in,
                check_out,
            )

        return super().filter_queryset(queryset)
