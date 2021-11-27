import factory


class ListingFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`listings.Listing`
    """

    class Meta:
        model = "listings.Listing"


class HotelRoomTypeFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`listings.HotelRoomType`
    """

    class Meta:
        model = "listings.HotelRoomType"


class HotelRoomFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`listings.HotelRoom`
    """

    class Meta:
        model = "listings.HotelRoom"


class BookingInfoFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`listings.BookingInfo`
    """

    class Meta:
        model = "listings.BookingInfo"


class BookingReservationFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`listings.BookingReservation`
    """

    class Meta:
        model = "listings.BookingReservation"
