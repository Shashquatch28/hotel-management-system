from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomerCreationForm, BookingForm
from .models import Hotel, Room, Booking
import datetime

# Home View
def home(request):
    return render(request, 'home.html')

# Register View
def register(request):
    if request.method == 'POST':
        # User is submitting the form
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save() # This creates and saves the new user
            # Redirect to the login page after successful registration
            return redirect('login') 
    else:
        # User is just visiting the page
        form = CustomerCreationForm()
    
    # Render the template with the form
    return render(request, 'register.html', {'form': form})

# Hotel View
def hotel_list(request):
    # This is the ORM query to get all hotels
    hotels = Hotel.objects.all() 
    
    # Pass the list of hotels to the template
    context = {
        'hotels': hotels
    }
    return render(request, 'hotel_list.html', context)

# Hotel Detail View
def hotel_detail(request, hotel_id):
    # Get the specific hotel by its ID. 
    # get_object_or_404 is a shortcut that automatically returns a 404 error if not found.
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    
    # Get all rooms that belong to this hotel
    rooms = Room.objects.filter(hotel=hotel)
    
    context = {
        'hotel': hotel,
        'rooms': rooms,
    }
    return render(request, 'hotel_detail.html', context)

# Protected Booking View
@login_required
def my_bookings(request):
    # This filters the Booking table to get only the ones
    # where 'cust' is the same as the user making the request.
    bookings = Booking.objects.filter(cust=request.user)
    
    context = {
        'bookings': bookings
    }
    return render(request, 'my_bookings.html', context)

# Booking Creation View
@login_required
def create_booking(request, hotel_id, room_number):
    # Find the specific room the user is trying to book
    room = get_object_or_404(Room, hotel_id=hotel_id, room_number=room_number)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False) # Don't save to DB yet
            booking.cust = request.user        # Set the customer
            
            # Set the room/hotel from the URL
            booking.hotel_id = room.hotel_id
            booking.room_number = room.room_number
            
            # Set other required fields
            booking.status = 'Confirmed'
            booking.bookingdate = datetime.date.today()
            
            booking.save() # Now, save the complete object
            
            return redirect('my-bookings') # Send to "My Bookings" page
    else:
        form = BookingForm() # Show a blank form

    context = {
        'form': form,
        'room': room,
    }
    return render(request, 'create_booking.html', context)