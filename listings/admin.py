from django.contrib import admin

from . import models


class HotelRoomTypeInline(admin.StackedInline):
    model = models.HotelRoomType
    extra = 1
    show_change_link = True


@admin.register(models.Listing)
class ListingAdmin(admin.ModelAdmin):
    inlines = [HotelRoomTypeInline]
    list_display = (
        "title",
        "listing_type",
        "country",
        "city",
    )
    list_filter = ("listing_type",)


class HotelRoomInline(admin.StackedInline):
    model = models.HotelRoom
    extra = 1


@admin.register(models.HotelRoomType)
class HotelRoomTypeAdmin(admin.ModelAdmin):
    inlines = [HotelRoomInline]
    list_display = (
        "hotel",
        "title",
    )
    show_change_link = True


@admin.register(models.HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ("room_number",)


@admin.register(models.BookingInfo)
class BookingInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BookingReservation)
class BookingReservationAdmin(admin.ModelAdmin):
    """
    Admin view for :model:`listings.BookingReservation`
    """

    list_display = ("booking_info", "start_date", "end_date")
