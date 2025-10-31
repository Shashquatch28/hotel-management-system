from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Booking
import datetime

# --- CustomerCreationForm (no changes) ---
class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = ('email', 'first_name', 'last_name')


# --- DateInput Widget (no changes) ---
class DateInput(forms.DateInput):
    input_type = 'date'


# --- BookingForm  ---
class BookingForm(forms.ModelForm):
    
    # 1. Add an __init__ method to accept the 'room'
    def __init__(self, *args, **kwargs):
        # Get the 'room' object passed from the view
        self.room = kwargs.pop('room', None) 
        super().__init__(*args, **kwargs)

    class Meta:
        model = Booking
        fields = ['checkin', 'checkout']
        widgets = {
            'checkin': DateInput(),
            'checkout': DateInput(),
        }

    def clean_checkin(self):
        checkin_date = self.cleaned_data.get('checkin')
        if checkin_date and checkin_date < datetime.date.today():
            raise forms.ValidationError("Check-in date cannot be in the past.")
        return checkin_date

    def clean(self):
        cleaned_data = super().clean()
        checkin_date = cleaned_data.get('checkin')
        checkout_date = cleaned_data.get('checkout')

        if checkin_date and checkout_date:
            if checkout_date <= checkin_date:
                raise forms.ValidationError(
                    "Check-out date must be after the check-in date."
                )

            if self.room: 
                # Find conflicting bookings
                conflicts = Booking.objects.filter(
                    hotel_id=self.room.hotel_id,
                    room_number=self.room.room_number, 
                    checkin__lt=checkout_date,
                    checkout__gt=checkin_date
                ).exclude(status='Cancelled')

                if self.instance and self.instance.pk:
                    conflicts = conflicts.exclude(pk=self.instance.pk)

                if conflicts.exists():
                    raise forms.ValidationError(
                        "This room is already booked for the selected dates."
                    )

        return cleaned_data