from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .forms import (
    CustomerCreationForm, BookingForm, ReviewForm, CustomerPhoneForm, 
    CustomerUpdateForm, CancellationForm
)
from .models import (
    Hotel, Room, Booking, Payment, Facility, Review, Offer, RoomImage, CustomerPhone, Offer, Cancellation
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
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login') 
    else:
        # User is just visiting the page
        form = CustomerCreationForm()
    
    # Render the template with the form
    return render(request, 'register.html', {'form': form})

# Hotel List View
def hotel_list(request):

    query = request.GET.get('q', '')
    # 3. Get the new filter from the URL
    offer_filter = request.GET.get('filter_offers')

    # 4. Start with all hotels
    hotels = Hotel.objects.all()

    # 5. Apply the search query first
    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )

    # 6. Apply the offer filter
    if offer_filter == 'on':
        today = datetime.date.today()
        # Filter hotels that have an active offer
        hotels = hotels.filter(
            offer__start_date__lte=today,
            offer__end_date__gte=today
        ).distinct() # .distinct() prevents duplicates

    # --- (This image logic is the same as before) ---
    all_room_images_query = RoomImage.objects.all()
    all_room_images = defaultdict(list)
    for image in all_room_images_query:
        all_room_images[image.hotel_id].append(image)

    for hotel in hotels:
        hotel.images = all_room_images.get(hotel.hotel_id, [])

    context = {
        'hotels': hotels,
        'search_query': query,
        'offer_filter': offer_filter, # 7. Pass the filter state to the template
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
            review.save()
            messages.success(request, 'Your review has been submitted. Thank you!')
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
    # 1. Get ALL bookings for the user.
    # 2. Use prefetch_related('payment_set') to efficiently get the payment.
    bookings = Booking.objects.filter(
        cust=request.user
    ).prefetch_related('payment_set').order_by('-checkin')
    
    # 3. Pass the single 'bookings' list to the template.
    context = {
        'bookings': bookings 
    }
    return render(request, 'my_bookings.html', context)

# Booking Creation View
@login_required
def create_booking(request, hotel_id, room_number):
    room = get_object_or_404(Room, hotel_id=hotel_id, room_number=room_number)

    if not room.availability:
        return render(request, 'room_not_available.html', {'room': room})
    
    if request.method == 'POST':
        # This is Step 1: User submitted the date form
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            checkin = form.cleaned_data['checkin']
            checkout = form.cleaned_data['checkout']
            
            # 2. Store the valid dates in the user's session
            request.session['booking_checkin'] = checkin.isoformat()
            request.session['booking_checkout'] = checkout.isoformat()
            
            # 3. Redirect to the new payment confirmation page
            return redirect('payment-confirmation', hotel_id=hotel_id, room_number=room_number)
    else:
        # This is the GET request (show the date form)
        form = BookingForm(room=room) 

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

    # Check if the booking is already cancelled
    if booking.status == 'Cancelled':
        messages.error(request, 'This booking has already been cancelled.')
        return redirect('my-bookings')

    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            # 1. Update Booking status
            booking.status = 'Cancelled'
            booking.save()
            
            # 2. Update Payment status
            try:
                payment = Payment.objects.get(booking=booking)
                payment.status = 'Cancelled'
                payment.save()
            except Payment.DoesNotExist:
                pass # No payment was found, which is fine
            
            # 3. Create the new Cancellation record
            cancellation = form.save(commit=False)
            cancellation.booking = booking
            cancellation.cancel_date = datetime.date.today()
            cancellation.save()
            
            messages.success(request, 'Your booking has been successfully cancelled.')
            return redirect('my-bookings')
    else:
        # GET request: Show the confirmation form
        form = CancellationForm()
    
    context = {
        'booking': booking,
        'form': form  # Pass the new form to the template
    }
    return render(request, 'cancel_booking.html', context)

# Edit Booking View
@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    room = get_object_or_404(Room, hotel_id=booking.hotel_id, room_number=booking.room_number)

    if booking.cust != request.user:
        return HttpResponseForbidden("You are not allowed to edit this booking.")

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, room=room)
        if form.is_valid():
            # Save the updated booking
            updated_booking = form.save() 
            
            try:
                # Find the related payment
                payment = Payment.objects.get(booking=updated_booking)
                
                # Recalculate the price
                num_nights = (updated_booking.checkout - updated_booking.checkin).days
                total_price = room.price * num_nights
                
                # Update the payment
                payment.amount = total_price
                payment.save()
                
            except Payment.DoesNotExist:
                # If no payment exists, you could create one
                pass

            messages.success(request, 'Your booking has been successfully updated.')
            return redirect('my-bookings')
    else:
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
            phone.save(force_insert=True)
            messages.success(request, 'Phone number added successfully.')
            return redirect('profile') # Redirect back to the profile page
    else:
        # Show a blank form
        form = CustomerPhoneForm()

    context = {
        'phones': phones,
        'form': form
    }
    return render(request, 'profile.html', context)

# --- 2. ADD THIS NEW VIEW ---
@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Load the form with POST data and the current user's instance
        form = CustomerUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile') # Redirect to profile page on success
    else:
        # Load the form with the current user's existing data
        form = CustomerUpdateForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'edit_profile.html', context)

# View to Delete Phone
@login_required
def delete_phone(request, cust_id, phone_number): # Accepts two arguments
    # 1. Use both fields to find the unique phone number
    phone = get_object_or_404(
        CustomerPhone, 
        cust_id=cust_id, 
        phone_number=phone_number
    )

    # 2. CRITICAL: Check if the logged-in user is the owner
    if phone.cust != request.user:
        return HttpResponseForbidden("You are not allowed to delete this phone number.")

    # We only want to delete if the form is POSTed
    if request.method == 'POST':
        phone.delete()
        messages.success(request, 'Phone number deleted.')
        return redirect('profile')
    
    # If it's a GET request, show confirmation
    context = {
        'phone': phone
    }
    return render(request, 'delete_phone.html', context)

#
# Delete Profile View
@login_required
def delete_profile(request):
    # We're deleting the user who is currently logged in
    user = request.user

    if request.method == 'POST':
        # This is the confirmation
        user.delete()
        logout(request) # Log them out as their account is gone
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home') # Send them to the home page

    # If it's a GET request, just show the confirmation page
    return render(request, 'delete_profile.html')

# Payment View
@login_required
def payment_confirmation(request, hotel_id, room_number):
    room = get_object_or_404(Room, hotel_id=hotel_id, room_number=room_number)
    
    # Get dates from the session
    checkin_str = request.session.get('booking_checkin')
    checkout_str = request.session.get('booking_checkout')
    
    # If session data is missing, send them back
    if not checkin_str or not checkout_str:
        messages.error(request, 'Something went wrong. Please select your dates again.')
        return redirect('create-booking', hotel_id=hotel_id, room_number=room_number)
        
    checkin = datetime.date.fromisoformat(checkin_str)
    checkout = datetime.date.fromisoformat(checkout_str)
    
    # Calculate price
    num_nights = (checkout - checkin).days
    subtotal = room.price * num_nights
    
    # Find the best active offer
    today = datetime.date.today()
    active_offer = Offer.objects.filter(
        hotel_id=hotel_id,
        start_date__lte=today,
        end_date__gte=today
    ).first() # Get the first valid offer
    
    discount = 0
    if active_offer:
        discount = subtotal * (active_offer.discount / 100)
        
    final_total = subtotal - discount

    # This is Step 2: User confirms the payment
    if request.method == 'POST':
        # Create the Booking and Payment
        try:
            booking = Booking.objects.create(
                cust=request.user,
                hotel_id=room.hotel_id,
                room_number=room.room_number,
                bookingdate=today,
                checkin=checkin,
                checkout=checkout,
                status='Confirmed'
            )
            
            Payment.objects.create(
                booking=booking,
                amount=final_total, # Save the FINAL discounted price
                mode='Card',
                date=today,
                status='Completed' # Mark as completed
            )
            
            # Clear the session data
            del request.session['booking_checkin']
            del request.session['booking_checkout']
            
            messages.success(request, 'Your booking is confirmed and payment is complete!')
            return redirect('my-bookings')
            
        except Exception as e:
            messages.error(request, 'An error occurred while confirming your booking.')
            return redirect('hotel-detail', hotel_id=hotel_id)

    # This is the GET request: show the confirmation page
    context = {
        'room': room,
        'checkin': checkin,
        'checkout': checkout,
        'num_nights': num_nights,
        'subtotal': subtotal,
        'active_offer': active_offer,
        'discount': discount,
        'final_total': final_total
    }
    return render(request, 'payment_confirmation.html', context)