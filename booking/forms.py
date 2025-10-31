from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        # These are the fields the user will fill out
        fields = ('email', 'first_name', 'last_name')