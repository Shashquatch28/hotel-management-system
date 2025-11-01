from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomerCreationForm, BookingForm, ReviewForm, CustomerPhoneForm
from .models import (
    Hotel, Room, Booking, Payment, Facility, Review, Offer, RoomImage, CustomerPhone
)
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

# Hotel List View
def hotel_list(request):
    hotels = Hotel.objects.all() 
    
    # 1. Get all room images and group them by hotel_id
    all_room_images_query = RoomImage.objects.all()
    all_room_images = defaultdict(list)
    for image in all_room_images_query:
        # This groups images by the hotel's ID
        all_room_images[image.hotel_id].append(image)

    # 2. Attach the list of images to each hotel object
    for hotel in hotels:
        hotel.images = all_room_images.get(hotel.hotel_id, []) # Get the list (or an empty list)

    context = {
        'hotels': hotels, # Pass the modified hotel objects
    }
    return render(request, 'hotel_list.html', context)

# Hotel Detail View (with Review Form)
def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.hotel = hotel
            review.cust = request.user
            review.date = datetime.date.today()
            if not review.rating:
                review.rating = 5.0 
            review.save()
            return redirect('hotel-detail', hotel_id=hotel_id)
    else:
        review_form = ReviewForm()

    
    # --- THIS IS THE UPDATED LOGIC ---
    rooms = Room.objects.filter(hotel=hotel)
    facilities = Facility.objects.filter(hotel=hotel)
    reviews = Review.objects.filter(hotel=hotel).order_by('-date')
    offers = Offer.objects.filter(hotel=hotel)
    
    # 1. Get images and group them by room_number
    room_images_query = RoomImage.objects.filter(hotel_id=hotel_id)
    room_images_dict = defaultdict(list)
    for image in room_images_query:
        room_images_dict[image.room_number].append(image)

    # 2. THIS IS THE NEW PART: Attach images to each room object
    for room in rooms:
        room.images = room_images_dict.get(room.room_number, [])

    context = {
        'hotel': hotel,
        'rooms': rooms, # Rooms now have .images attached
        'facilities': facilities,
        'reviews': reviews,
        'offers': offers,
        'review_form': review_form,
        # We no longer need to pass room_images
    }
    return render(request, 'hotel_detail.html', context)

# "My Bookings" View
@login_required
def my_bookings(request):
    # Get bookings only for the currently logged-in user
    bookings = Booking.objects.filter(cust=request.user)
    
    context = {
        'bookings': bookings
    }
    return render(request, 'my_bookings.html', context)

# Booking Creation View
@login_required
def create_booking(request, hotel_id, room_number):
    room = get_object_or_404(Room, hotel_id=hotel_id, room_number=room_number)

    # Check Room Availability
    if not room.availability:
        return render(request, 'room_not_available.html', {'room': room})
    
    if request.method == 'POST':
        form = BookingForm(request.POST, room=room) # Pass room for validation
        if form.is_valid():
            booking = form.save(commit=False)
            booking.cust = request.user      
            booking.hotel_id = room.hotel_id
            booking.room_number = room.room_number
            booking.status = 'Confirmed'
            booking.bookingdate = datetime.date.today()
            
            booking.save() # Save booking to get an ID
            
            # Calculate Payment for Booking
            try:
                num_nights = (booking.checkout - booking.checkin).days
                total_price = room.price * num_nights

                Payment.objects.create(
                    booking=booking,
                    amount=total_price,
                    mode='Card',
                    date=datetime.date.today(),
                    status='Pending'
                )
            except Exception as e:
                # If payment fails, delete the booking to avoid orphans
                booking.delete()
                # In a real app, you'd show an error page
                return redirect('home')

            return redirect('my-bookings') # Send to "My Bookings" page
    else:
        form = BookingForm(room=room) # Pass room for validation

    context = {
        'form': form,
        'room': room,
    }
    return render(request, 'create_booking.html', context)

# View to Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if the logged-in user is the owner
    if booking.cust != request.user:
        return HttpResponseForbidden("You are not allowed to cancel this booking.")

    if request.method == 'POST':
        booking.delete()
        # You might also want to update the associated Payment status to 'Cancelled'
        return redirect('my-bookings')
    
    # If it's a GET request, show a confirmation page
    context = {
        'booking': booking
    }
    return render(request, 'cancel_booking.html', context)

# Edit Booking View
@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Find the specific room for this booking
    room = get_object_or_404(Room, hotel_id=booking.hotel_id, room_number=booking.room_number)

    # Check if the logged-in user is the owner
    if booking.cust != request.user:
        return HttpResponseForbidden("You are not allowed to edit this booking.")

    if request.method == 'POST':
        # Pass the 'room' object for validation
        form = BookingForm(request.POST, instance=booking, room=room)
        if form.is_valid():
            form.save() # Save the changes to the existing object
            # You might want to update the Payment object here too
            return redirect('my-bookings')
    else:
        # Pass the 'room' object for validation
        form = BookingForm(instance=booking, room=room)

    context = {
        'form': form,
        'booking': booking
    }
    return render(request, 'edit_booking.html', context)


# User Profile View
@login_required
def profile(request):
    # Get all phone numbers for the current user
    phones = CustomerPhone.objects.filter(cust=request.user)

    if request.method == 'POST':
        # User is adding a new phone number
        form = CustomerPhoneForm(request.POST)
        if form.is_valid():
            phone = form.save(commit=False)
            phone.cust = request.user  # Link the phone to the user
            phone.save()
            return redirect('profile') # Redirect back to the profile page
    else:
        # Show a blank form
        form = CustomerPhoneForm()

    context = {
        'phones': phones,
        'form': form
    }
    return render(request, 'profile.html', context)

# View to Delete Phone
@login_required
def delete_phone(request, phone_id):
    # Find the phone number
    phone = get_object_or_404(CustomerPhone, pk=phone_id)

    # CRITICAL: Check if the logged-in user is the owner
    if phone.cust != request.user:
        return HttpResponseForbidden("You are not allowed to delete this phone number.")

    # We only want to delete if the form is POSTed
    if request.method == 'POST':
        phone.delete()
        # Redirect back to the profile page
        return redirect('profile')
    
    # If it's a GET request, just show a confirmation page
    context = {
        'phone': phone
    }
    return render(request, 'delete_phone.html', context)