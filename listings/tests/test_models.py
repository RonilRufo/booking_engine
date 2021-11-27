from django.test import TestCase

from .mixins import ListingsTestMixin


class ListingsModelTests(ListingsTestMixin, TestCase):
    """
    Contains a collection of tests for models in listings app.
    """

    def test_hotel_room_str(self):
        """
        Test successful response for __str__ method in HotelRoom model.
        """
        hotel_room_type = self.create_hotel_room_type()
        room = self.create_hotel_room(hotel_room_type=hotel_room_type)
        self.assertEqual(str(room), str(room.room_number))
