from typing import Dict, List, Union

from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from . import models
from .mixins import RepresentationMixin


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer class for :model:`listings.Listing`
    """

    class Meta:
        model = models.Listing
        fields = (
            "id",
            "listing_type",
            "title",
            "country",
            "city",
        )
        read_only_fields = ("id",)


class HotelRoomTypeSerializer(RepresentationMixin, serializers.ModelSerializer):
    """
    Serializer class for :model:`listings.HotelRoomType`
    """

    class Meta:
        model = models.HotelRoomType
        fields = (
            "id",
            "hotel",
            "title",
        )
        read_only_fields = ("id",)
        nested_serializers = [
            {
                "field": "hotel",
                "serializer_class": ListingSerializer,
            }
        ]


class BookingInfoSerializer(RepresentationMixin, serializers.ModelSerializer):
    """
    Serializer class for :model:`listings.BookingInfo`
    """

    title = serializers.SerializerMethodField()
    listing_type = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    class Meta:
        model = models.BookingInfo
        fields = (
            "id",
            "listing",
            "title",
            "listing_type",
            "country",
            "city",
            "hotel_room_type",
            "price",
        )
        read_only_fields = ("id",)
        nested_serializers = [
            {
                "field": "listing",
                "serializer_class": ListingSerializer,
            },
            {
                "field": "hotel_room_type",
                "serializer_class": HotelRoomTypeSerializer,
            },
        ]

    def get_title(self, obj: models.BookingInfo) -> str:
        """
        Returns the title of the related listing/hotel room type for this instance.
        """
        return obj.listing.title if obj.listing else str(obj.hotel_room_type)

    def get_listing_type(self, obj: models.BookingInfo) -> str:
        """
        Returns whether this instance is a Hotel or an Apartment.
        """
        return (
            models.Listing.APARTMENT.title()
            if obj.listing
            else models.Listing.HOTEL.title()
        )

    def get_country(self, obj: models.BookingInfo) -> str:
        """
        Returns the country of the related base listing for this instance.
        """
        return obj.listing.country if obj.listing else obj.hotel_room_type.hotel.country

    def get_city(self, obj: models.BookingInfo) -> str:
        """
        Returns the city of the related base listing for this instance.
        """
        return obj.listing.city if obj.listing else obj.hotel_room_type.hotel.city


class BookingReservationSerializer(RepresentationMixin, serializers.ModelSerializer):
    """
    Serializer class for :model:`listings.BookingReservation`
    """

    class Meta:
        model = models.BookingReservation
        fields = (
            "id",
            "booking_info",
            "start_date",
            "end_date",
        )
        read_only_fields = ("id",)

    def validate(self, data: Dict) -> Dict:
        """
        Custom validation to check for valid start_date and end_date values along with
        room availability.
        """
        # start date must not be later than end date
        if data.get("start_date") > data.get("end_date"):
            raise serializers.ValidationError(
                _("start_date must not be later than end_date.")
            )

        # Check room availability
        booking_info = data.get("booking_info")
        overlapping_reservations: Union[
            QuerySet, List[models.BookingReservation]
        ] = booking_info.reservations.filter(
            Q(
                start_date__lte=data.get("start_date"),
                end_date__gte=data.get("start_date"),
            )
            | Q(
                start_date__lte=data.get("end_date"),
                end_date__gte=data.get("end_date"),
            )
            | Q(
                start_date__gte=data.get("start_date"),
                end_date__lte=data.get("end_date"),
            )
            | Q(
                start_date__lte=data.get("start_date"),
                end_date__gte=data.get("end_date"),
            )
        ).distinct()

        total_rooms = (
            1
            if booking_info.listing
            else booking_info.hotel_room_type.hotel_rooms.count()
        )
        available_rooms = total_rooms - overlapping_reservations.count()

        if available_rooms <= 0:
            raise serializers.ValidationError(
                _(
                    "Rooms are fully booked for the specified date range. Please try a "
                    "different date range."
                )
            )

        return data
