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
