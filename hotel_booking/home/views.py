
from django.contrib import messages
from django.contrib.auth.hashers import make_password
# from home.models import UserProfile
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import * 
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.core.paginator import Paginator
from datetime import date
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import UserProfile, Booking, Location
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import requests
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.html import strip_tags
from django.contrib import messages
from django.utils.dateparse import parse_date 


# @login_required
def index(request):
    return render(request, 'index.html')

@login_required
def room(request):
    rooms = Room.objects.all()  # Fetch all rooms
    return render(request, 'room.html', {'rooms': rooms})
@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'room_detail.html', {'room': room})

def service(request):
    return render(request, 'service.html')
def team(request):
    return render(request, 'team.html')
def testmonial(request):
    return render(request, 'testmonial.html')
def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == "POST":
        # Retrieve form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("number")  # Match model field name
        password = request.POST.get("password")

        # Check for duplicate username, email, or phone number
        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect("register")

        if UserProfile.objects.filter(number=phone_number).exists():
            messages.error(request, "Phone number already in use")
            return redirect("register")

        # Create and save the user with a hashed password
        # UserProfile.objects.create(
        #     username=username,
        #     email=email,
        #     number=phone_number,
        #     password=make_password(password)  # Hashing password before saving
        # )
        
        hashed_password = make_password(password)  # Hash the password before saving

        user = UserProfile(username=username, email=email,number=phone_number, password=hashed_password)
        user.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")  # Redirect to login page

    return render(request, "register.html")  # Handle GET request properly


def loginn(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_profile = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("login")

        if check_password(password, user_profile.password):  
            request.session['user_id'] = user_profile.id  
            request.session['username'] = user_profile.username  
            
            # 🔹 Make Django recognize this user as logged in
            user_profile.backend = 'django.contrib.auth.backends.ModelBackend'  # Required for login()
            login(request, user_profile)

            messages.success(request, f"Welcome, {user_profile.username}! You have successfully logged in.")
            return redirect("index")  # Redirect to the hotel room page
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

    return render(request, "login.html")

def user_logout(request):
    logout(request) 
    return redirect('login') 


@login_required
def booking_page(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'booking.html', {'room': room})

def booking_success_view(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    # Get most booked subcategories (popular hotels/rooms)
    most_booked = SubCategory.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:4]

    context = {
        'booking': booking,
        'user': request.user,
        'most_booked': most_booked,  # ✅ Make sure this line exists
    }

    return render(request, 'room.html', context)

def show_location_dropdown(request):
    locations = Location.objects.all()

    return render(request, 'room.html', {'locations': locations})
def Recommendations(request):
    # Get the location with the highest number of bookings
    most_booked_location = Location.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count').first()

    # Get rooms in that location
    rooms = Room.objects.filter(location=most_booked_location)

    locations = Location.objects.all()
    categories = Category.objects.all()

    context = {
        'rooms': rooms,
        'most_booked_location': most_booked_location,
        'locations': locations,
        'categories': categories,
    }
    return render(request, 'MostRecommendations.html', context)

def room_list(request):
    location = request.GET.get('location')
    category = request.GET.get('category')

    rooms = Room.objects.all()

    if location:
        rooms = rooms.filter(location__location_name__icontains=location)

    if category:
        rooms = rooms.filter(subcategory__category__category_name__icontains=category)

    locations = Location.objects.all()
    categories = Category.objects.all()

    context = {
        'rooms': rooms,
        'locations': locations,
        'categories': categories,
        'selected_location': location,
        'selected_category': category,
    }
    return render(request, 'room.html', context)


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")

        if not checkin or not checkout:
            return JsonResponse({'error': 'Missing check-in or check-out date'}, status=400)

        from datetime import datetime
        date_format = "%Y-%m-%d"
        start = datetime.strptime(checkin, date_format)
        end = datetime.strptime(checkout, date_format)
        number_of_days = (end - start).days
        if number_of_days <= 0:
            return JsonResponse({'error': 'Invalid date range'}, status=400)

        
        
        
        party_type = request.POST.get("party_type")  # indoor/outdoor
        indoor_people = request.POST.get("indoor_people")
        outdoor_place = request.POST.get("outdoor_place")

        party_amount = 0

        
        if party_type == "indoor":
                if indoor_people == "100":
                    party_amount = 10000
                elif indoor_people == "150":
                    party_amount = 15000
                elif indoor_people == "200":
                    party_amount = 20000
        elif party_type == "outdoor":
                if outdoor_place == "beach":
                    party_amount = 25000
                elif outdoor_place == "courtyard":
                    party_amount = 20000

        base_amount = room.room_rent * number_of_days

        guide = request.POST.get("guide") == "on"
        vehicle = request.POST.get("vehicle") == "on"
        gym = request.POST.get("gym") == "on"

        guide_amount = 1000 * number_of_days if guide else 0
        vehicle_amount = 1000 * number_of_days if vehicle else 0
        gym_amount = 2000 * number_of_days if gym else 0

        # total amount
        total_amount = base_amount + guide_amount + vehicle_amount + gym_amount + party_amount

        try:
            # Create Booking entry in DB
            # Create Booking entry in DB
            booking = Booking.objects.create(
            user=request.user,
            room=room,
            location=room.location,
            category=room.subcategory.category,
            subcategory=room.subcategory,
            amount=total_amount,
            checkin=checkin,
            checkout=checkout,
            guide=guide,
            vehicle=vehicle,
            gym=gym,
            
            party_type=party_type,
            indoor_people_count=indoor_people if indoor_people else None,
            outdoor_place=outdoor_place if outdoor_place else None,
            payment_method='razorpay',
            status='booked',
        )


            # ✅ Decrease available room count by 1
            if room.available_room > 0:
                room.available_room -= 1
                room.save()
            else:
                return JsonResponse({'error': 'No rooms available'}, status=400)

            
            # ✅ Send Booking Confirmation Email to Owner (You)
            try:
                subject = "New Booking Confirmation"
                message = f"""
                        New booking received!

                        User: {request.user.username}
                        Email: {request.user.email}
                        Room: {room.name}
                        Check-in: {checkin}
                        Check-out: {checkout}
                        Total Amount: ₹{total_amount}

                        Services:
                        - Guide: {'Yes' if guide else 'No'}
                        - Vehicle: {'Yes' if vehicle else 'No'}
                        - Gym: {'Yes' if gym else 'No'}

                        Booking ID: {booking.booking_id}
                                        """
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,  # From
                    [settings.EMAIL_HOST_USER],  # To (your email)
                    fail_silently=False
                )
                messages.success(request, "Booking email sent successfully!")
            except Exception as e:
                print(f"❌ Email sending failed: {e}")
                messages.error(request, f"Email error: {e}")

            # ✅ Razorpay Payment Order
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({
                "amount": int(total_amount * 100),
                "currency": "INR",
                "receipt": str(booking.booking_id),
                "payment_capture": 1
            })

            return JsonResponse({
                "razorpay_order_id": payment['id'],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "currency": "INR",
                "totalAmount": total_amount,
                "booking_id": str(booking.booking_id)
            })

        except Exception as e:
            print(f"Error during booking: {e}")
            return JsonResponse({'error': 'Booking creation failed'}, status=500)

    return render(request, 'room.html', {"room": room})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'success.html', {'booking': booking})

@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room', 'category', 'subcategory', 'location').order_by('-checkin')

    paginator = Paginator(bookings, 5)  # Show 5 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bookings.html', {'bookings': page_obj})
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == "booked":
        booking.status = "cancelled"
        booking.save()
    return redirect(request.META.get('HTTP_REFERER', 'bookings_today'))

def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    # Set the response and content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.booking_id}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Invoice content
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, 800, "Booking Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Booking ID: {booking.booking_id}")
    p.drawString(50, 740, f"Customer: {booking.user.username}")
    p.drawString(50, 720, f"Email: {booking.user.email}")
    p.drawString(50, 700, f"Location: {booking.location.location_name}")
    p.drawString(50, 680, f"Category: {booking.category.category_name}")
    p.drawString(50, 660, f"Subcategory: {booking.subcategory.subcategory_name}")
    p.drawString(50, 640, f"Room: {booking.room}")
    p.drawString(50, 620, f"Check-in: {booking.checkin}")
    p.drawString(50, 600, f"Check-out: {booking.checkout}")
    p.drawString(50, 580, f"Amount Paid: ₹{booking.amount}")
    p.drawString(50, 560, f"Payment Method: {booking.payment_method.title()}")
    p.drawString(50, 540, f"Booking Status: {booking.status}")

    # Footer
    p.drawString(50, 100, "Thank you for choosing Hotelier!")

    p.showPage()
    p.save()

    return response
def add_review(request):
    bookings = Booking.objects.filter(user=request.user, status='checked_out')
    return render(request, 'add_review.html',  {'bookings': bookings})

@login_required
def submit_review(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('review')

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if hasattr(booking, 'review'):
            messages.warning(request, 'Review already exists for this booking.')
            return redirect('add_review')

        Review.objects.create(
            booking=booking,
            user=request.user,
            rating=int(rating),
            comment=comment
        )

        messages.success(request, 'Thank you! Your review has been submitted.')
        return redirect('add_review')

    return redirect('home') # Fallback redirect


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        
        # If the user is authenticated, link the message to the user
        user = request.user if request.user.is_authenticated else None

        # Save to database
        contact = Contact.objects.create(
            user=user,
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Send email to the owner
        owner_email = "sreayarajan75@gmail.com"  # ✅ Your email as the recipient

        try:
            send_mail(
                f"New Contact Form Submission: {subject}",
                f"From: {name} ({email})\n\nMessage:\n{message}",
                "sreayarajan75@gmail.com",  # ✅ Use your own email as the sender (EMAIL_HOST_USER)
                [owner_email],  # ✅ Send to your own email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")

        return redirect("contact")  # Redirect to the contact page after submission

    return render(request, "contact.html")

def get_coordinates(location_name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}"
    response = requests.get(url, headers={"User-Agent": "YourAppName"})
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

def get_nearby_places(lat, lon, tags):
    overpass_url = "http://overpass-api.de/api/interpreter"
    radius = 3000  # 3km radius

    queries = ''.join([
        f'node["{tag.split("=")[0]}"="{tag.split("=")[1]}"](around:{radius},{lat},{lon});'
        for tag in tags
    ])

    query = f"""
    [out:json];
    (
      {queries}
    );
    out center;
    """

    response = requests.post(overpass_url, data=query.encode("utf-8"), headers={"User-Agent": "YourAppName"})
    data = response.json()

    print("Tags being searched:", tags)
    print("Coordinates:", lat, lon)
    print("Query:", query)
    print("Raw response:", data)

    places = []
    for element in data["elements"]:
            tags_data = element.get("tags", {})
            name = tags_data.get("name", "Unnamed Place")
            lat = element.get("lat")
            lon = element.get("lon")
            places.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "tags": tags_data
            })

    return places


def location_recommendations(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    location_name = booking.location.location_name

    lat, lon = get_coordinates("Bangalore")
    print(lat, lon)


    if not lat or not lon:
        return render(request, 'recommendations.html', {'error': 'Location not found.'})

    beautiful_places = get_nearby_places(lat, lon, ["tourism=attraction", "leisure=park", "natural=peak"])
    restaurants = get_nearby_places(lat, lon, ["amenity=restaurant", "amenity=cafe"])

    return render(request, 'recommendations.html', {
        "location": location_name,
        "beautiful_places": beautiful_places,
        "restaurants": restaurants
    })















#ADMIN SIDE
def index1(request):
    return render(request, 'adminside/index1.html')

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")  # Change to email
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)  # Authenticate with email

        if user is not None and user.is_superuser:  # Ensure only superusers can log in
            login(request, user)
            return redirect('dashboard')  # Redirect to the admin dashboard
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, "adminside/admin_login.html")

def admin_logout(request):
    request.session.flush()  # Clears all session data
    logout(request)  # Logs out the user
    return redirect("admin_login") 
@login_required

def dashboard(request):
    return render(request, "adminside/dashboard.html")

def dashboard(request):
    today = date.today()
    
    users_today = UserProfile.objects.filter(is_staff=False).count()
    bookings_today = Booking.objects.filter(created_at__date=today).count()
    upcoming_bookings = Booking.objects.filter(checkin__gt=today).count()

    # Yearly bookings grouped by month
    year_bookings = Booking.objects.filter(created_at__year=today.year).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id'))

    # Most booked location
    most_booked_location = Booking.objects.values('location__location_name').annotate(total=Count('id')).order_by('-total').first()

    context = {
        'users_today': users_today,
        'bookings_today': bookings_today,
        'upcoming_bookings': upcoming_bookings,
        'year_bookings': list(year_bookings),
        'most_booked_location': most_booked_location,
    }
    return render(request, "adminside/dashboard.html", context)

def customers_list(request):
    customers = UserProfile.objects.filter(is_staff=False)
    return render(request, 'adminside/ourCustomers.html', {'customers': customers})
def bookings_today_list(request):
    today = date.today()
    bookings = Booking.objects.filter(created_at__date=today)
    return render(request, 'adminside/bookingtoday.html', {'bookings': bookings})

def upcoming_bookings_list(request):
    today = date.today()
    bookings = Booking.objects.filter(checkin__gt=today, status='booked')
    return render(request, 'adminside/upcoming_bookings.html', {'bookings': bookings})

def top_location_bookings(request):
    top_location = Booking.objects.values('location__location_name').annotate(total=Count('id')).order_by('-total').first()
    bookings = Booking.objects.filter(location__location_name=top_location['location__location_name'])
    return render(request, 'adminside/top_location.html', {'bookings': bookings, 'location': top_location['location__location_name']})

def admin_bookings(request):
    selected_location_id = request.GET.get('location')
    
    bookings_list = Booking.objects.all().order_by('-created_at')

    if selected_location_id:
        bookings_list = bookings_list.filter(location_id=selected_location_id)

    paginator = Paginator(bookings_list, 8)  # Show 8 bookings per page
    page_number = request.GET.get("page")
    bookings = paginator.get_page(page_number)

    locations = Location.objects.all()  # Fetch all locations

    return render(request, "adminside/adminbookings.html", {
        "bookings": bookings,
        "locations": locations,
        "selected_location_id": int(selected_location_id) if selected_location_id else None
    })
@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.is_staff: 
        new_status = request.POST.get('status')
        if new_status in dict(STATUS_CHOICES).keys():
            booking.status = new_status
            booking.save()
            messages.success(request, "Booking status updated.")
        else:
            messages.error(request, "Invalid status.")
    else:
        messages.error(request, "Unauthorized.")

    return redirect('admin_bookings') 


@login_required(login_url="admin_login")
def manage_location(request):
    if request.method == "POST":
        if "location_id" in request.POST:  # If updating
            location_id = request.POST.get("location_id")
            location_name = request.POST.get("location_name")
            location = get_object_or_404(Location, id=location_id)
            location.location_name = location_name
            location.save()
        elif "delete_id" in request.POST:  # If deleting
            location_id = request.POST.get("delete_id")
            location = get_object_or_404(Location, id=location_id)
            location.delete()
        else:  # If creating a new location
            location_name = request.POST.get("location_name")
            if location_name:
                Location.objects.create(location_name=location_name)

        return redirect("manage_location")

    locations = Location.objects.all()
    return render(request, "adminside/location.html", {"locations": locations})

def manage_category(request):
    locations = Location.objects.all()
    categories = Category.objects.select_related('location_name').all()

    if request.method == 'POST':
        if 'add_category' in request.POST:
            location_id = request.POST.get('location_id')
            category_name = request.POST.get('category_name')
            if location_id and category_name:
                location = Location.objects.get(id=location_id)
                Category.objects.create(location_name=location, category_name=category_name)
                return redirect('manage_category')

        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category_name = request.POST.get('category_name')
            category = Category.objects.get(id=category_id)
            category.category_name = category_name
            category.save()
            return redirect('manage_category')

        elif 'delete_category' in request.POST:
            category_id = request.POST.get('delete_id')
            Category.objects.get(id=category_id).delete()
            return redirect('manage_category')

    return render(request, 'adminside/category.html', {'locations': locations, 'categories': categories})


def manage_category(request):
    locations = Location.objects.all()
    categories = Category.objects.select_related('location_name').all()

    if request.method == 'POST':
        if 'add_category' in request.POST:
            location_id = request.POST.get('location_id')
            category_name = request.POST.get('category_name')
            location = get_object_or_404(Location, id=location_id)
            Category.objects.create(location_name=location, category_name=category_name)
            return redirect('manage_category')

        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category_name = request.POST.get('category_name')
            category = get_object_or_404(Category, id=category_id)
            category.category_name = category_name
            category.save()
            return redirect('manage_category')

        elif 'delete_category' in request.POST:
            delete_id = request.POST.get('delete_id')
            Category.objects.filter(id=delete_id).delete()
            return redirect('manage_category')

    return render(request, 'adminside/category.html', {
        'locations': locations,
        'categories': categories,
    })

def manage_category(request):
    locations = Location.objects.all()
    categories = Category.objects.select_related('location_name').all()

    if request.method == 'POST':
        if 'add_category' in request.POST:
            location_id = request.POST.get('location_id')
            category_name = request.POST.get('category_name')
            location = get_object_or_404(Location, id=location_id)
            Category.objects.create(location_name=location, category_name=category_name)
            return redirect('manage_category')

        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category_name = request.POST.get('category_name')
            category = get_object_or_404(Category, id=category_id)
            category.category_name = category_name
            category.save()
            return redirect('manage_category')

        elif 'delete_category' in request.POST:
            delete_id = request.POST.get('delete_id')
            Category.objects.filter(id=delete_id).delete()
            return redirect('manage_category')

    return render(request, 'adminside/category.html', {
        'locations': locations,
        'categories': categories,
    })


def manage_subcategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    location = category.location_name
    subcategories = SubCategory.objects.filter(category=category)

    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name')

        if 'add_subcategory' in request.POST and subcategory_name:
            # ✅ Add new subcategory
            SubCategory.objects.create(
                category=category,
                subcategory_name=subcategory_name
            )
            return redirect('manage_subcategory', category_id=category_id)

        elif 'update_subcategory' in request.POST:
            subcategory_id = request.POST.get('subcategory_id')
            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            subcategory.subcategory_name = subcategory_name
            subcategory.save()
            return redirect('manage_subcategory', category_id=category_id)

        elif 'delete_subcategory' in request.POST:
            subcategory_id = request.POST.get('delete_id')
            SubCategory.objects.filter(id=subcategory_id).delete()
            return redirect('manage_subcategory', category_id=category_id)

    return render(request, 'adminside/subcategory.html', {
        'category': category,
        'location': location,
        'subcategories': subcategories,
    })
    

def room_details(request):
    if request.method == "POST":
        if "delete_room" in request.POST:
            room_id = request.POST.get("delete_id")
            room = get_object_or_404(Room, id=room_id)
            room.images.all().delete()  # Delete related images
            room.delete()
            return redirect("room_details")

    rooms = Room.objects.all()
    return render(request, "adminside/room__details.html", {"rooms": rooms})


# def manage_room(request):
#     selected_location_id = request.GET.get("location", "")  # Get selected location from request
#     locations = Location.objects.all()
    
#     # Fetch only the subcategories related to the selected location
#     if selected_location_id:
#         subcategories = SubCategory.objects.filter(location_id=selected_location_id)
#     else:
#         subcategories = SubCategory.objects.none()  # Show empty initially
    
#     if request.method == "POST":
#         if "add_room" in request.POST:
#             subcategory_id = request.POST.get("subcategory")
#             location_id = request.POST.get("location")
#             room_rent = request.POST.get("room_rent")
#             room_details = request.POST.get("room_details")
#             available_room = request.POST.get("available_room")
#             room_images = request.FILES.getlist("room_images")  # Get multiple files

#             subcategory = get_object_or_404(SubCategory, id=subcategory_id)
#             location = get_object_or_404(Location, id=location_id)

#             # Create the Room instance
#             room = Room.objects.create(
#                 subcategory=subcategory,
#                 location=location,
#                 room_rent=room_rent,
#                 room_details=room_details,
#                 available_room=available_room,
#             )

#             # Save multiple images linked to the room
#             for image in room_images:
#                 RoomImage.objects.create(room=room, image=image)

#             return redirect("room_rate")

#     return render(
#         request,
#         "adminside/room_rate.html",
#         {
#             "locations": locations,
#             "subcategories": subcategories,
#             "selected_location_id": selected_location_id,
#         },
#     )



def manage_room(request):
    # Get selected location from request (either POST or GET)
    selected_location_id = request.POST.get("location") or request.GET.get("location", "")
    
    locations = Location.objects.all()
    
    # Initialize subcategories queryset
    subcategories = SubCategory.objects.none()
    
    # If a location is selected, filter subcategories
    if selected_location_id:
        subcategories = SubCategory.objects.filter(category__location_name__id=selected_location_id)


    
    if request.method == "POST":
        if "add_room" in request.POST:
            subcategory_id = request.POST.get("subcategory")
            location_id = request.POST.get("location")
            room_rent = request.POST.get("room_rent")
            room_details = request.POST.get("room_details")
            available_room = request.POST.get("available_room")
            room_images = request.FILES.getlist("room_images")

            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            location = get_object_or_404(Location, id=location_id)

            # Create the Room instance
            room = Room.objects.create(
                subcategory=subcategory,
                location=location,
                room_rent=room_rent,
                room_details=room_details,
                available_room=available_room,
            )

            # Save multiple images
            for image in room_images:
                RoomImage.objects.create(room=room, image=image)

            return redirect("room_rate")

    return render(
        request,
        "adminside/room_rate.html",
        {
            "locations": locations,
            "subcategories": subcategories,
            "selected_location_id": selected_location_id,
        },
    )

def apply_discount(request):
    if request.method == "POST" and "apply_discount" in request.POST:
        room_id = request.POST.get("room_id")
        room = get_object_or_404(Room, id=room_id)

        start_date = parse_date(request.POST.get("start_date"))
        end_date = parse_date(request.POST.get("end_date"))
        discount_percentage = int(request.POST.get("discount_percentage"))
        coupon_code = request.POST.get("coupon_code")

        Discount.objects.create(
            room=room,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage,
            coupon_code=coupon_code,
            active=True
        )

        messages.success(request, "Discount successfully applied!")
        return redirect("room_details")
def contact_data(request):
    all_contacts = Contact.objects.all().order_by('-created_at')  # Latest first
    return render(request, "adminside/contact_data.html", {"contacts": all_contacts})
