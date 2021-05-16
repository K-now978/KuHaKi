from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import ListView
from django.contrib import  messages
from .models import Section, Seat, Reservation
from accounts.models import User

import datetime
from django.utils import timezone

from random import *
import json

def get_rest_time(seat):
    if not seat.available:
        return -1

    elif seat.booked:
        now = timezone.now()
        usage_seconds = (now - seat.booked.start_time).total_seconds()
        available_seconds = seat.booked.time
        if usage_seconds >= available_seconds:
            Reservation.remove_reservation(seat)
            return 0
        else:
            # percent of rest time.
            return ((available_seconds - usage_seconds)/available_seconds*100)
    else:
        return 0

def seatlist(request):
    context = {}
    s_n = {}
    for section in Section.objects.all():
        seats = Seat.objects.filter(section=section).order_by('number')
        seats_dict = {}
        for seat in seats:
            seats_dict[seat.number] = get_rest_time(seat)
        s_n[f'{section}'] = seats_dict
        
    if hasattr(request.user, 'reservation'):
        reserve = request.user.reservation
        my_seat = reserve.seat
        now = timezone.now()
        usage_seconds = (now - reserve.start_time).total_seconds()
        available_seconds = reserve.time

        if usage_seconds >= available_seconds:
            context['my_seat'] = None
            Reservation.remove_reservation(reserve)
        else:
            tmp = dict()
            tmp['section'] = str(my_seat.section)
            tmp['number'] = my_seat.number
            context['my_seat'] = tmp
    else:
        context['my_seat'] = None

    context["section_names"] = s_n

    return render(request, 'seat_list.html', context)

def makeautcode(request):
    if request.method == 'GET':
        file_path = "./auth.json"
        context = {}
        authnumber = randint(1000,9999)
        code = authnumber
        context['authnum'] = str(authnumber)
        with open(file_path,'w') as json_file:
            json.dump(context, json_file)
        return render(request, 'authnumber.html', context)

def reserveseat(request):
    if request.method == 'GET':         
        authcode = request.GET['authNum']
        file_path = "./auth.json"
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
            authNum = json_data['authnum']
       
        if authcode == authNum:

            
            section_name = request.GET['section']
            section = Section.objects.filter(name=section_name)[0]
            number = request.GET['number']
            time = request.GET['time']
            current_user = request.user
            
            seats = Seat.objects.filter(section=section, number=number)
            seat = seats[0]
            if not seat.booked == None:
                messages.info(request, '예약된 좌석입니다.')
            else:
                booking = Reservation(user=current_user, time=time, start_time=timezone.now())
                booking.save()
                seat.booked = booking
                seat.save()
        else:
            messages.info(request, '틀린 Auth Code입니다.')
    return redirect('login')

def extendseat(request):
    if request.method == 'GET':         
        authcode = request.GET['authNum']
        file_path = "./auth.json"
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
            authNum = json_data['authnum']
       
        if authcode == authNum:
            time = request.GET['time']
            current_user = request.user

            if not hasattr(current_user, 'reservation'):
                messages.info(request, '좌석 예약시간이 초과하였습니다.')
            else:
                booking = current_user.reservation

                now = timezone.now()
                available_seconds = booking.time
                usage_seconds = (now - booking.start_time).total_seconds()
                if (available_seconds - usage_seconds) <= 1800:
                    booking.time += int(time)
                booking.save()
        else:
            messages.info(request, '틀린 Auth Code입니다.')
    return redirect('login')

def moveseat(request):
    if request.method == 'GET':
        section_name = request.GET['section']
        section = Section.objects.filter(name=section_name)[0]
        number = request.GET['number']
        current_user = request.user
        if not hasattr(current_user, 'reservation'):
            messages.info(request, '좌석 예약시간이 초과하였습니다.')
        else:
            seats = Seat.objects.filter(section=section, number=number)
            seat = seats[0]

            booking = current_user.reservation #Reservation(user=current_user, time=time)
            new_booking = Reservation(user=current_user, time=booking.time, start_time=booking.start_time)
            booking.delete()
            new_booking.save()

            seat.booked = new_booking
            seat.save()
            messages.info(request, '좌석이 변경되었습니다.')

    return redirect('login')

def returnseat(request):
    Reservation.remove_reservation(request.user)
    return redirect('login')

# Create your views here.
#def seats(request):
#    return render(request, 'seats.html')