from django.urls import path
from . import views
from .views import booking_success


urlpatterns = [
    path('', views.index, name='index'), 
    path("register/", views.register, name="register"),
    path("login/", views.loginn, name="login"),
    path('logout/', views.user_logout, name='logout'),
    path("room/",views.room,name="room"),
    path('dropdown-test/', views.show_location_dropdown, name='dropdown_test'),
    path('rooms/', views.room_list, name='room_list'),
    path('room_detail/<int:room_id>/', views.room_detail, name='room_detail'),
    path('booking/<int:room_id>/',views.booking_page, name='booking_page'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path("booking-success/<uuid:booking_id>/", views.booking_success, name="booking_success"),
    path('my-bookings/', views.user_bookings, name='user_bookings'),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("download-invoice/<uuid:booking_id>/", views.download_invoice, name="download_invoice"),
    path('add_review/', views.add_review, name='add_review'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path("contact/",views.contact,name="contact"),
    path("service/",views.service,name="service"),
    path("team/",views.team,name="team"),
    path("testmonial/",views.testmonial,name="testmonial"),
    path("about/",views.about,name="about"),
    path('recommendations/<int:booking_id>/', views.location_recommendations, name='location_recommendations'),
    path('Mostrecommendations/', views.Recommendations, name='Recommendations'),


    
#ADMIN SIDE
 path('index1', views.index1, name='index1'), 
 path('admin_login/', views.admin_login, name='admin_login'),
 path("admin_logout/", views.admin_logout, name="admin_logout"),
 path('dashboard/', views.dashboard, name='dashboard'),
 path('customers/', views.customers_list, name='customers_list'),
 
    path('bookings-today/', views.bookings_today_list, name='bookings_today'),
    path('upcoming-bookings/', views.upcoming_bookings_list, name='upcoming_bookings'),
    path('top-location/', views.top_location_bookings, name='top_location'),
 path('admin_bookings/', views.admin_bookings, name='admin_bookings'),
 path('booking/<int:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
path("location/", views.manage_location, name="manage_location"),
path("category/", views.manage_category, name="manage_category"),
path('subcategory/<int:category_id>/', views.manage_subcategory, name='manage_subcategory'),

path("room_rate/", views.manage_room, name="room_rate"),
path("room_details/", views.room_details, name="room_details"),
# path('room-discount/<int:room_id>/', views.set_room_discount, name='set_room_discount'),
path('apply-discount/', views.apply_discount, name='apply_discount'),
path('contact_data/', views.contact_data, name='contact_data'),



 
]
