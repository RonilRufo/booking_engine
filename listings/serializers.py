from rest_framework import serializers

from . import models
from .mixins import RepresentationMixin


class HotelRoomTypeSerializer(serializers.ModelSerializer):
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
