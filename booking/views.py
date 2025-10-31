from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
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
        form = BookingForm(request.POST, room = room)
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
        form = BookingForm(room = room) # Show a blank form

    context = {
        'form': form,
        'room': room,
    }
    return render(request, 'create_booking.html', context)

# View to Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    # Find the booking
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # CRITICAL: Check if the logged-in user is the owner
    if booking.cust != request.user:
        # If not, return a "Forbidden" error
        return HttpResponseForbidden("You are not allowed to cancel this booking.")

    # We only want to delete if the form is POSTed
    if request.method == 'POST':
        booking.delete()
        # Redirect back to the list of bookings
        return redirect('my-bookings')
    
    # If it's a GET request, just show a confirmation page
    context = {
        'booking': booking
    }
    return render(request, 'cancel_booking.html', context)

# Edit View
@login_required
def edit_booking(request, booking_id):
    # Find the existing booking
    booking = get_object_or_404(Booking, pk=booking_id)

    # Check if the logged-in user is the owner
    if booking.cust != request.user:
        return HttpResponseForbidden("You are not allowed to edit this booking.")

    if request.method == 'POST':
        # Load the form with the new POST data AND the existing booking instance
        form = BookingForm(request.POST, instance=booking, room = Room)
        if form.is_valid():
            form.save() # Save the changes to the existing object
            return redirect('my-bookings')
    else:
        # Load the form with the existing booking's data
        # This is what pre-populates the fields
        form = BookingForm(instance=booking)

    context = {
        'form': form,
        'booking': booking
    }
    return render(request, 'edit_booking.html', context)