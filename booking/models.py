from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ---------------------------------- Booking Model ----------------------------------
class Booking(models.Model):
    booking_id = models.AutoField(db_column='Booking_ID', primary_key=True)  # Field name made lowercase.
    cust = models.ForeignKey('Customer', models.CASCADE, db_column='Cust_ID', blank=True, null=True)  # Field name made lowercase.
    hotel_id = models.IntegerField(db_column='Hotel_ID', blank=True, null=True)
    room_number = models.CharField(db_column='Room_Number', max_length=10, blank=True, null=True)
    bookingdate = models.DateField(db_column='BookingDate', blank=True, null=True)  # Field name made lowercase.
    checkin = models.DateField(db_column='CheckIn', blank=True, null=True)  # Field name made lowercase.
    checkout = models.DateField(db_column='CheckOut', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'booking'


# ---------------------------------- Customer Model ----------------------------------
class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # This hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# ---------------------------------- Cancellation Model ----------------------------------
class Cancellation(models.Model):
    cancellation_id = models.AutoField(db_column='Cancellation_ID', primary_key=True)  # Field name made lowercase.
    booking = models.ForeignKey(Booking, models.CASCADE, db_column='Booking_ID', blank=True, null=True)  # Field name made lowercase.
    cancel_date = models.DateField(db_column='Cancel_Date', blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cancellation'


# ---------------------------------- Customer Model ----------------------------------
class Customer(AbstractBaseUser, PermissionsMixin): 
    cust_id = models.AutoField(db_column='Cust_ID', primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    dateofbirth = models.DateField(db_column='DateOfBirth', blank=True, null=True)
    email = models.CharField(db_column='Email', unique=True, max_length=100) 
    city = models.CharField(db_column='City', max_length=255, blank=True, null=True)
    state = models.CharField(db_column='State', max_length=255, blank=True, null=True)
    country = models.CharField(db_column='Country', max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()  

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        managed = False
        db_table = 'customer'


# ---------------------------------- Customer Phone Model ----------------------------------
class CustomerPhone(models.Model):
    pk = models.CompositePrimaryKey('cust', 'phone_number')
    cust = models.ForeignKey(Customer, models.CASCADE, db_column='Cust_ID')  # Field name made lowercase.
    phone_number = models.CharField(db_column='Phone_Number', max_length=20)  # Field name made lowercase.
    is_primary = models.BooleanField(db_column='Is_Primary', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer_phone'


# ---------------------------------- Facility Model ----------------------------------
class Facility(models.Model):
    facility_id = models.AutoField(db_column='Facility_ID', primary_key=True)  # Field name made lowercase.
    hotel = models.ForeignKey('Hotel', models.CASCADE, db_column='Hotel_ID', blank=True, null=True)  # Field name made lowercase.
    facility_name = models.CharField(db_column='Facility_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'facility'


# ---------------------------------- Hotel Model ----------------------------------
class Hotel(models.Model):
    hotel_id = models.AutoField(db_column='Hotel_ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=255, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rating = models.DecimalField(db_column='Rating', max_digits=2, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    contact = models.CharField(db_column='Contact', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'hotel'


# ---------------------------------- Offer Model ----------------------------------
class Offer(models.Model):
    offer_id = models.AutoField(db_column='Offer_ID', primary_key=True)  # Field name made lowercase.
    hotel = models.ForeignKey(Hotel, models.CASCADE, db_column='Hotel_ID', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_Date', blank=True, null=True)  # Field name made lowercase.
    end_date = models.DateField(db_column='End_Date', blank=True, null=True)  # Field name made lowercase.
    discount = models.DecimalField(db_column='Discount', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'offer'


# ---------------------------------- Payment Model ----------------------------------
class Payment(models.Model):
    payment_id = models.AutoField(db_column='Payment_ID', primary_key=True)  # Field name made lowercase.
    booking = models.ForeignKey(Booking, models.CASCADE, db_column='Booking_ID', blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mode = models.CharField(db_column='Mode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'payment'


# ---------------------------------- Review Model ----------------------------------
class Review(models.Model):
    review_id = models.AutoField(db_column='Review_ID', primary_key=True)  # Field name made lowercase.
    cust = models.ForeignKey(Customer, models.CASCADE, db_column='Cust_ID', blank=True, null=True)  # Field name made lowercase.
    hotel = models.ForeignKey(Hotel, models.CASCADE, db_column='Hotel_ID', blank=True, null=True)  # Field name made lowercase.
    rating = models.DecimalField(db_column='Rating', max_digits=2, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    comment = models.CharField(db_column='Comment', max_length=255, blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'review'


# ---------------------------------- Room Model ----------------------------------
class Room(models.Model):
    pk = models.CompositePrimaryKey('hotel', 'room_number')
    hotel = models.ForeignKey(Hotel, models.CASCADE, db_column='Hotel_ID')  # Field name made lowercase.
    room_number = models.CharField(db_column='Room_Number', max_length=10)  # Field name made lowercase.
    roomtype = models.CharField(db_column='RoomType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    capacity = models.IntegerField(db_column='Capacity', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    availability = models.BooleanField(db_column='Availability', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'room'


# ---------------------------------- Room Image Model ----------------------------------
class RoomImage(models.Model):
    pk = models.CompositePrimaryKey('hotel_id', 'room_number', 'image_url')
    hotel_id = models.IntegerField(db_column='Hotel_ID')
    room_number = models.CharField(db_column='Room_Number', max_length=10)
    image_url = models.CharField(db_column='Image_URL', max_length=255)  # Field name made lowercase.
    reference_name = models.CharField(db_column='Reference_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'room_image'