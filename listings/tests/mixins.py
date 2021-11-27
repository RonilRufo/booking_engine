import random

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from faker import Faker

from .. import models
from .factories import (
    BookingInfoFactory,
    BookingReservationFactory,
    HotelRoomFactory,
    HotelRoomTypeFactory,
    ListingFactory,
)


class ListingsTestMixin:
    def __init__(self, *args, **kwargs):
        self.fake = Faker()
        super(ListingsTestMixin, self).__init__(*args, **kwargs)

    def create_listing(self, **kwargs) -> models.Listing:
        """
        Creates an instance of :model:`listings.Listing` with dummy data.
        """
        if "title" not in kwargs:
            kwargs.update({"title": self.fake.name()})

        if "listing_type" not in kwargs:
            choices = [choice[0] for choice in models.Listing.LISTING_TYPE_CHOICES]
            kwargs.update({"listing_type": random.choice(choices)})

        if "country" not in kwargs:
            kwargs.update({"country": self.fake.country()})

        if "city" not in kwargs:
            kwargs.update({"city": self.fake.city()})

        return ListingFactory.create(**kwargs)

    def create_hotel_room_type(self, **kwargs) -> models.HotelRoomType:
        """
        Creates an instance of :model:`listings.HotelRoomType` with dummy data.
        """
        if "hotel" not in kwargs:
            kwargs.update(
                {"hotel": self.create_listing(listing_type=models.Listing.HOTEL)}
            )

        if "title" not in kwargs:
            kwargs.update({"title": self.fake.name()})

        return HotelRoomTypeFactory.create(**kwargs)

    def create_hotel_room(self, **kwargs) -> models.HotelRoom:
        """
        Creates an instance of :model:`listings.HotelRoom` with dummy data.
        """
        if "hotel_room_type" not in kwargs:
            kwargs.update({"hotel_room_type": self.create_hotel_room_type()})

        if "room_number" not in kwargs:
            kwargs.update({"room_number": random.randint(100, 999)})

        return HotelRoomFactory.create(**kwargs)

    def create_booking_info(self, **kwargs) -> models.BookingInfo:
        """
        Creates an instance of :model:`listings.BookingInfo` with dummy data.
        """
        if "listing" not in kwargs and "hotel_room_type" not in kwargs:
            choices = [choice[0] for choice in models.Listing.LISTING_TYPE_CHOICES]
            listing_type = random.choice(choices)
            if listing_type == models.Listing.APARTMENT:
                kwargs.update(
                    {"listing": self.create_listing(listing_type=listing_type)}
                )
            else:
                kwargs.update({"hotel_room_type": self.create_hotel_room_type()})

        if "price" not in kwargs:
            kwargs.update({"price": random.randint(50, 500)})

        return BookingInfoFactory.create(**kwargs)

    def create_booking_reservation(self, **kwargs) -> models.BookingReservation:
        """
        Creates an instance of :model:`listings.BookingReservation` with dummy data.
        """
        if "booking_info" not in kwargs:
            kwargs.update({"booking_info": self.create_booking_info()})

        if "start_date" not in kwargs:
            kwargs.update(
                {
                    "start_date": (
                        timezone.now() + relativedelta(days=random.randint(1, 30))
                    ).date()
                }
            )

        if "end_date" not in kwargs:
            kwargs.update(
                {
                    "end_date": kwargs.get("start_date")
                    + relativedelta(days=random.randint(1, 5))
                }
            )

        return BookingReservationFactory.create(**kwargs)
