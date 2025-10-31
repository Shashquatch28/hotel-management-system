from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Booking


class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        # These are the fields the user will fill out
        fields = ('email', 'first_name', 'last_name')


# Widget for date-picker
class DateInput(forms.DateInput):
    input_type = 'date'


# Booking Form 
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # These are the only two fields the user should fill out
        fields = ['checkin', 'checkout']
        # Use our new date-picker widget
        widgets = {
            'checkin': DateInput(),
            'checkout': DateInput(),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # These are the only two fields the user should fill out
        fields = ['checkin', 'checkout']
        # Use our new date-picker widget
        widgets = {
            'checkin': DateInput(),
            'checkout': DateInput(),
        }