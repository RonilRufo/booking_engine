import random

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .mixins import ListingsTestMixin


class BookingReservationTests(ListingsTestMixin, APITestCase):
    """
    Test cases for `reservations` endpoints(:views:`listings.BookingReservationViewSet`)
    """

    def test_create_booking_reservation(self):
        """
        Test successful creation of a booking reservation.
        """
        booking_info = self.create_booking_info()
        start_date = (timezone.now() + relativedelta(days=3)).date()
        end_date = start_date + relativedelta(days=2)
        payload = {
            "booking_info": booking_info.id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

        url = reverse("reservations-list")
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_booking_reservation_detail(self):
        """
        Test successful response in retrieving a single booking reservation.
        """
        reservation = self.create_booking_reservation()
        url = reverse("reservations-detail", args=(reservation.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], reservation.id)

    def test_list_booking_reservations(self):
        """
        Test successful response in retrieving a list of booking reservations.
        """
        reservations = [
            self.create_booking_reservation() for _ in range(random.randint(3, 7))
        ]

        url = reverse("reservations-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reservations), len(response.data))
