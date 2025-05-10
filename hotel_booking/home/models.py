from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from datetime import date
from decimal import Decimal
import uuid


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username, number, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), username=username, number=number)
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, number, password):
        user = self.create_user(email, username, number, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=15, unique=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'  # Login using email instead of username
    REQUIRED_FIELDS = ['username', 'number']  # Required when creating a superuser

    def __str__(self):
        return self.email
    
    
class Location(models.Model):
    location_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.location_name

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    location_name = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return f"{self.category_name} - {self.location_name}"
    
class SubCategory(models.Model):
    subcategory_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
  
    def __str__(self):
        return f"{self.subcategory_name} ({self.category.category_name})"
    

class Room(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='rooms')
    room_rent = models.DecimalField(max_digits=10, decimal_places=2)
    room_details = models.TextField()
    available_room = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="rooms", default=1) 
    def __str__(self):
        return f"{self.location.location_name} - {self.subcategory.subcategory_name} - {self.room_rent}"
    
    def get_discounted_rent(self):
        today = now().date()
        active_discount = self.discounts.filter(
            start_date__lte=today, end_date__gte=today, active=True
        ).first()

        if active_discount:
            discount_percent = Decimal(active_discount.discount_percentage) / Decimal('100')
            discounted_rent = self.room_rent * (Decimal('1.0') - discount_percent)
            return discounted_rent.quantize(Decimal('0.01'))  # round to 2 decimal places
        return self.room_rent
    
    def has_active_discount(self):
        today = now().date()
        return self.discounts.filter(start_date__lte=today, end_date__gte=today, active=True).exists()

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')

    def __str__(self):
        return f"Image for {self.room.subcategory.subcategory_name}"
STATUS_CHOICES = [
    ('booked', 'Booked'),
    ('checked_in', 'Checked In'),
    ('checked_out', 'Checked Out'),
    ('cancelled', 'Cancelled'),
]
    
User = get_user_model()   
class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='bookings')
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='bookings')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='bookings')
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE, related_name='bookings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkin = models.DateField(null=False, blank=False)
    checkout = models.DateField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, default='razorpay', editable=False)
    guide = models.BooleanField(default=False)
    vehicle = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='booked'
    )
    party_type = models.CharField(max_length=20, choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')], blank=True, null=True)
    indoor_people_count = models.IntegerField(blank=True, null=True)  # 100, 150, 200
    outdoor_place = models.CharField(max_length=50, blank=True, null=True)  # Beach, Courtyard


    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"    
    
class Contact(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)  # Foreign key added
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject    
    
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for Booking {self.booking.booking_id}"
    
class Discount(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='discounts')
    discount_percentage = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    coupon_code = models.CharField(max_length=50, blank=True, null=True)  # Optional
    active = models.BooleanField(default=True)

    def is_valid(self):
        return self.active and self.start_date <= date.today() <= self.end_date

    def __str__(self):
        return f"{self.room} - {self.discount_percentage}% off"    
    
    