from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .models import *


# Create your views here.
def home(request):
    amenities_objs = Amenties.objects.all()
    hotels_objs = Hotel.objects.all()
    hotels_images = HotelImages.objects.all()
    print(hotels_images)
    sort_by = request.GET.get('sort_by')
    if sort_by:
        if sort_by == 'ASC':
            hotels_objs = hotels_objs.order_by('hotel_price')
        elif sort_by == 'DSC':
            hotels_objs = hotels_objs.order_by(F('hotel_price').desc())

    search = request.GET.get('search')
    if search:
        hotels_objs = hotels_objs.filter(
            Q(hotel_name__icontains=search) |
            Q(description__icontains=search) |
            Q(amenties__amenity_name__icontains=search)).distinct()

    amenities = request.GET.getlist('amenities')
    if len(amenities):
        hotels_objs = hotels_objs.filter(amenties__amenity_name__in=amenities)

    context = {"amenities_objs": amenities_objs, "hotels_objs": hotels_objs, 'sort_by': sort_by, 'search': search,
               'amenities': amenities, 'hotels_images': hotels_images}
    return render(request, 'hotel.html', context)


def check_booking(start_date, end_date, uid, room_count):
    qs = HotelBooking.objects.filter(
        start_date__lte=start_date,
        end_date__gte=end_date,
        hotel__uid=uid
    )

    if len(qs) >= room_count:
        return False

    return True


def hotel_detail(request, uid):
    hotel_obj = Hotel.objects.get(uid=uid)

    if request.method == 'POST':
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        hotel = Hotel.objects.get(uid=uid)
        if not check_booking(checkin, checkout, uid, hotel.room_count):
            messages.warning(request, 'Hotel is already booked in these dates ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        HotelBooking.objects.create(hotel=hotel, user=request.user, start_date=checkin, end_date=checkout,
                                    booking_type='Pre Paid')

        messages.success(request, 'Your booking has been saved')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'hotel_detail.html', {'hotels_obj': hotel_obj})


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user_obj = authenticate(username=username, password=password)
        if not user_obj:
            messages.warning(request, 'Invalid password ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        login(request, user_obj)
        return redirect('/')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username)

        if user_obj.exists():
            messages.warning(request, 'Username already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
        return redirect('/')

    return render(request, 'register.html')
