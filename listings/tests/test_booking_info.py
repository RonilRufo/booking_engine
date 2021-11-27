import random
import urllib
from decimal import Decimal
from typing import Dict, List

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import BookingInfo, Listing
from .mixins import ListingsTestMixin


class BookingInfoTests(ListingsTestMixin, APITestCase):
    """
    Test cases for `units` endpoints(:views:`listings.BookingInfoViewSet`)
    """

    def test_retrieve_booking_info(self):
        """
        Test successful response in retrieving a single booking reservation.
        """
        unit = self.create_booking_info()
        url = reverse("units-detail", args=(unit.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], unit.id)

    def test_list_booking_info(self):
        """
        Test successful response in retrieving a list of available units.
        """
        units = [self.create_booking_info() for _ in range(random.randint(3, 7))]

        url = reverse("units-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(units), len(response.data))

        # Test sort by price ascending
        previous_unit: Dict = None
        for unit in response.data:
            if previous_unit is None:
                previous_unit = unit
                continue

            self.assertLessEqual(
                Decimal(previous_unit["price"]),
                Decimal(unit["price"]),
            )
            previous_unit = unit

    def test_filter_max_price(self):
        """
        Test successful response in filtering units by `max_price` in the list endpoint.
        """
        max_price = 100
        below_max_price_units: List[BookingInfo] = [
            self.create_booking_info(price=random.randint(20, 100))
            for _ in range(random.randint(3, 9))
        ]
        unit_ids: List[int] = [unit.id for unit in below_max_price_units]

        # Create units/booking info instance with prices above max_price
        [self.create_booking_info(price=max_price + 1) for _ in range(2, 5)]

        query_params = urllib.parse.urlencode({"max_price": max_price})
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(below_max_price_units), len(response.data))

        previous_unit: Dict = None
        for unit in response.data:
            self.assertIn(unit["id"], unit_ids)

            if previous_unit is None:
                previous_unit = unit
                continue

            self.assertLessEqual(
                Decimal(previous_unit["price"]),
                Decimal(unit["price"]),
            )
            previous_unit = unit

    def test_filter_check_in_and_check_out_filter(self):
        """
        Test successful response in filtering units by `check_in` and `check_out` in the
        list endpoint.
        """
        now = timezone.now().date()
        check_in = now + relativedelta(days=3)
        check_out = check_in + relativedelta(days=2)

        booked_apartment = self.create_listing(listing_type=Listing.APARTMENT)
        available_apartment = self.create_listing(listing_type=Listing.APARTMENT)

        five_star_hotel = self.create_listing(listing_type=Listing.HOTEL)
        three_star_hotel = self.create_listing(listing_type=Listing.HOTEL)

        # Create booking info for the apartments
        booked_apartment_booking = self.create_booking_info(listing=booked_apartment)
        available_apartment_booking = self.create_booking_info(
            listing=available_apartment
        )

        # Create a reservation for booked apartment
        self.create_booking_reservation(
            booking_info=booked_apartment_booking,
            start_date=check_in - relativedelta(days=1),
            end_date=check_out + relativedelta(days=1),
        )

        # Create 2 hotel rooms and room types for `five_star_hotel`
        five_star_single = self.create_hotel_room_type(hotel=five_star_hotel)
        [self.create_hotel_room(hotel_room_type=five_star_single) for _ in range(2)]
        five_star_single_booking = self.create_booking_info(
            hotel_room_type=five_star_single
        )

        five_star_double = self.create_hotel_room_type(hotel=five_star_hotel)
        [self.create_hotel_room(hotel_room_type=five_star_double) for _ in range(3)]
        five_star_double_booking = self.create_booking_info(
            hotel_room_type=five_star_double
        )

        # Create a reservation for 1 hotel room in 5 star hotel
        self.create_booking_reservation(
            booking_info=five_star_single_booking,
            start_date=check_in + relativedelta(days=1),
            end_date=check_in + relativedelta(days=1),
        )

        # Create 2 hotel rooms and 1 room type for `three_star_hotel`
        three_star_single = self.create_hotel_room_type(hotel=three_star_hotel)
        [self.create_hotel_room(hotel_room_type=three_star_single) for _ in range(2)]
        three_star_single_booking = self.create_booking_info(
            hotel_room_type=three_star_single
        )

        # Create a reservation for each single room making the single room type fully
        # booked in 3 star hotel
        self.create_booking_reservation(
            booking_info=three_star_single_booking,
            start_date=now,
            end_date=check_in + relativedelta(days=1),
        )
        self.create_booking_reservation(
            booking_info=three_star_single_booking,
            start_date=check_in + relativedelta(days=1),
            end_date=check_out + relativedelta(days=2),
        )

        query_params = urllib.parse.urlencode(
            {
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
            }
        )
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unit_ids = [unit["id"] for unit in response.data]
        self.assertNotIn(booked_apartment_booking.id, unit_ids)
        self.assertIn(available_apartment_booking.id, unit_ids)
        self.assertIn(five_star_single_booking.id, unit_ids)
        self.assertIn(five_star_double_booking.id, unit_ids)
        self.assertNotIn(three_star_single_booking.id, unit_ids)

        # ensure that units are sorted by price in ascending order
        previous_unit: Dict = None
        for unit in response.data:
            if previous_unit is None:
                previous_unit = unit
                continue

            self.assertLessEqual(
                Decimal(previous_unit["price"]),
                Decimal(unit["price"]),
            )
            previous_unit = unit

    def test_filter_hotel_multiple_rooms(self):
        """
        This covers the test cases presented in the README file.

        For covering more test cases we are going to need at least one hotel with 3
        Hotel Room Types:

            1. First with price=50 (below max_price) with blocked day inside the search
            criteria for all rooms(could be 1 room)

            2. Second with price=60 (below max_price) with blocked day inside the search
            criteria for one out of few rooms

            3. Third with price 200 (above max_price)

        """
        hotel = self.create_listing(listing_type=Listing.HOTEL)
        now = timezone.now().date()
        check_in = now + relativedelta(days=2)
        check_out = check_in + relativedelta(days=3)

        # Create 3 room types
        single_room_type = self.create_hotel_room_type(hotel=hotel)
        double_room_type = self.create_hotel_room_type(hotel=hotel)
        suite_room_type = self.create_hotel_room_type(hotel=hotel)

        # create 1 room for single room type
        self.create_hotel_room(hotel_room_type=single_room_type)

        # Create booking info for single room type
        single_room_booking = self.create_booking_info(
            hotel_room_type=single_room_type,
            price=50,
        )

        # Create reservation inside the `check_in` and `check_out` range for single room
        # type.
        self.create_booking_reservation(
            booking_info=single_room_booking,
            start_date=check_in + relativedelta(days=1),
            end_date=check_out - relativedelta(days=1),
        )

        # create 2 rooms for double room type
        [self.create_hotel_room(hotel_room_type=double_room_type) for _ in range(2)]

        # Create booking info for double room type
        double_room_booking = self.create_booking_info(
            hotel_room_type=double_room_type,
            price=60,
        )

        # Create reservation inside `check_in` and `check_out` range for double room
        # type. Only 1 hotel room will be covered. Note that there are 2 hotel rooms
        # for double room type.
        self.create_booking_reservation(
            booking_info=single_room_booking,
            start_date=check_in + relativedelta(days=1),
            end_date=check_out - relativedelta(days=1),
        )

        # Create another reservation for the remaining double room but the date range
        # will be outside of the given date range.
        self.create_booking_reservation(
            booking_info=single_room_booking,
            start_date=check_out + relativedelta(days=10),
            end_date=check_out + relativedelta(days=15),
        )

        # create 2 rooms for suite room type
        [self.create_hotel_room(hotel_room_type=suite_room_type) for _ in range(2)]

        # Create booking info for suite room type
        suite_room_booking = self.create_booking_info(
            hotel_room_type=suite_room_type,
            price=200,
        )

        query_params = urllib.parse.urlencode(
            {
                "max_price": 100,
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
            }
        )
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unit_ids = [unit["id"] for unit in response.data]

        # Suite rooms are priced at 200 which is over the max_price. It should not be
        # available.
        self.assertNotIn(suite_room_booking.id, unit_ids)

        # Single room type only has 1 room and it has a reservation inside the given
        # date range. It should not be available.
        self.assertNotIn(single_room_booking.id, unit_ids)

        # Double room type has 2 rooms and only 1 has a reservation inside the given
        # date range. It should be available.
        self.assertIn(double_room_booking.id, unit_ids)

    def test_filter_units_missing_check_out(self):
        """
        Test raising ValidationError when filtering units by `check_in` but `check_out`
        value is missing.
        """
        now = timezone.now().date()
        check_in = now + relativedelta(days=3)
        query_params = urllib.parse.urlencode(
            {"check_in": check_in.strftime("%Y-%m-%d")}
        )
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_units_missing_check_in(self):
        """
        Test raising ValidationError when filtering units by `check_out` but `check_in`
        value is missing.
        """
        now = timezone.now().date()
        check_out = now + relativedelta(days=3)
        query_params = urllib.parse.urlencode(
            {"check_out": check_out.strftime("%Y-%m-%d")}
        )
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_units_check_in_greater_than_check_out(self):
        """
        Test raising ValidationError when `check_in` value is greater than `check_out`
        value.
        """
        now = timezone.now().date()
        check_in = now + relativedelta(days=3)
        check_out = check_in - relativedelta(days=1)
        query_params = urllib.parse.urlencode(
            {
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
            }
        )
        url = reverse("units-list")
        response = self.client.get(f"{url}?{query_params}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookingInfoModelTests(ListingsTestMixin, APITestCase):
    """
    Test cases for :model:`listings.BookingInfo`
    """

    def test_booking_info_apartment_str(self):
        """
        Test __str__ method for apartment type booking info.
        """
        apartment = self.create_listing(listing_type=Listing.APARTMENT)
        booking = self.create_booking_info(listing=apartment)

        self.assertEqual(f"{str(apartment)} {booking.price}", str(booking))

    def test_booking_info_hotel_str(self):
        """
        Test __str__ method for hotel type booking info.
        """
        hotel = self.create_listing(listing_type=Listing.HOTEL)
        hotel_room_type = self.create_hotel_room_type(hotel=hotel)
        booking = self.create_booking_info(hotel_room_type=hotel_room_type)

        self.assertEqual(f"{str(hotel_room_type)} {booking.price}", str(booking))
