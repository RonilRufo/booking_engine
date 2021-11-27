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

    class Meta:
        model = models.BookingInfo
        fields = (
            "id",
            "listing",
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
