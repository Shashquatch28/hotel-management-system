from django.contrib import admin
from .models import (
    Customer, CustomerPhone, Hotel, Room, Booking, Payment, Review,
    RoomImage, Facility, Cancellation, Offer
)

# --- Inlines for Composite Key Models ---
# This lets you edit CustomerPhone from the Customer admin page
class CustomerPhoneInline(admin.TabularInline):
    model = CustomerPhone
    extra = 1  # Shows 1 blank form by default

# This lets you edit Room from the Hotel admin page
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

# --- Admin Classes for Parent Models ---
class CustomerAdmin(admin.ModelAdmin):
    inlines = [CustomerPhoneInline]  # Add the phone inline here
    # You can add more customizations later
    list_display = ('email', 'first_name', 'last_name', 'is_staff')

class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomInline]  # Add the room inline here
    list_display = ('name', 'city', 'rating')

# --- Register Parent Models with their new Admin Classes ---
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Hotel, HotelAdmin)

# --- Register all other normal models ---
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Facility)
admin.site.register(Cancellation)
admin.site.register(Offer)

# --- Models we CANNOT register ---
# These models have composite keys and are NOT registered.
# We edit CustomerPhone and Room using the inlines above.
# RoomImage also has a composite key and cannot be registered.
# For now, it must be omitted from the admin.
#
# admin.site.register(CustomerPhone) # <-- This caused the error
# admin.site.register(Room)          # <-- This would also cause an error
# admin.site.register(RoomImage)     # <-- This would also cause an error