from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import  messages
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.utils import timezone
from seats.models import Section, Seat
from accounts.models import Student
from accounts.models import User
import re

from .utils import get_rest_time


# Create your views here.

def administrtor(request):
    context = {}
    hsstudent_list = []
    for student_info in Student.objects.all():
        if student_info.student_name == "superuser": continue
        hsstudent_list.append(student_info)
    context["student_info"]=hsstudent_list
    
    if request.user.is_staff:
        return render(request, 'manager.html',context)
    else:
        messages.info(request, 'Not Authorized')
        return redirect('login')

@csrf_exempt
def add_list(request):
    if request.user.is_staff:
        if request.method == 'POST':
            p = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$') ## 이메일 형식을 확인하기
            hslist = json.loads(request.body)
            count = 0
            error = 0
            total = len(hslist)
            for infor in hslist:
                email = infor[0]
                student_name = infor[1]
                student_id = infor[2]

                if not Student.objects.filter(email=email).exists() and not Student.objects.filter(student_id=student_id).exists():
                    if p.match(email) != None:
                        if(len(student_id) == 10):
                            ## user에 이메일이 등록안된 경우 --> 등록시켜줘야함 
                            Student(student_name=student_name,email=email,student_id=student_id).save()
                            count+=1
                        else:
                            error+=1
                    else:
                        error+=1
            exists = total - count - error


        return HttpResponse(["총 : {}\n추가 성공 : {}\n실패 : {}\n이미 존재하는 데이터 : {}\n"
        .format(total,count,error,exists)])
    else :         
        messages.info(request, 'Not Authorized')
        return redirect('login')

@csrf_exempt
def del_list(request):
    if request.user.is_staff:
        if request.method == 'POST':
            delist = json.loads(request.body)
            count = 0
            for infor in delist:
                email = infor[0]
                student_name = infor[1]
                student_id = infor[2]
            

                if Student.objects.filter(email=email).exists():
                    Student.objects.filter(email=email).delete()
                    count+=1
                    
        return HttpResponse(["삭제 : " ,count])
    
    else : return redirect('login')


def available_seats(request):
    if not request.user.is_staff:
        messages.info(request, 'Not Authorized')
        return redirect('login')

    context = {}
    s_n = {}
    for section in Section.objects.all():
        seats = Seat.objects.filter(section=section).order_by('number')
        seats_dict = {}
        for seat in seats:
            seats_dict[str(seat.number)] = get_rest_time(seat)
        s_n[f'{section}'] = seats_dict
        
    if hasattr(request.user, 'reservation'):
        reserve = request.user.reservation
        my_seat = reserve.seat
        now = timezone.now()
        usage_seconds = (now - reserve.start_time).total_seconds()
        available_seconds = reserve.time

        if usage_seconds >= available_seconds:
            context["my_seat"] = None
            Reservation.remove_reservation(reserve)
        else:
            tmp = dict()
            tmp["section"] = str(my_seat.section)
            tmp["number"] = my_seat.number
            context["my_seat"] = tmp
    else:
        context["my_seat"] = None

    context["section_names"] = s_n

    return render(request, 'available_seats.html', context)

def available_seats_change(request):
    if not request.user.is_staff:
        messages.info(request, 'Not Authorized')
        return redirect('login')

    av_seats = json.loads(request.POST.get('av_seats'))
    uav_seats = json.loads(request.POST.get('uav_seats'))
    change_count = 0

    for a_s in av_seats:
        section = a_s.split('-')[1]
        seat = a_s.split('-')[3]
        section = Section.objects.get(name=section)
        seat = Seat.objects.get(section=section, number=seat)
        if seat.available == False:
            seat.available = True
            seat.save()
            change_count += 1

    for ua_s in uav_seats:
        section = ua_s.split('-')[1]
        seat = ua_s.split('-')[3]
        section = Section.objects.get(name=section)
        seat = Seat.objects.get(section=section, number=seat)
        if seat.available == True:
            seat.available = False
            seat.save()
            change_count += 1

    return HttpResponse(json.dumps({"result": change_count}, cls=DjangoJSONEncoder), content_type = "application/json")

def user_list(request):
    context = {}
    hsstudent_list = []
    for student_info in User.objects.all():
        if student_info.is_staff : continue
        hsstudent_list.append(student_info)
    context["user_info"]=hsstudent_list
    
    if request.user.is_staff:
        return render(request, 'user_list.html',context)
    else:
        messages.info(request, 'Not Authorized')
        return redirect('login')

@csrf_exempt
def del_userlist(request):
    if request.user.is_staff:
        if request.method == 'POST':
            delist = json.loads(request.body)
            count = 0
            for infor in delist:
                student_name = infor[0]
                email = infor[1]
                student_id = infor[2]
            
                if User.objects.filter(email=email).exists():
                    User.objects.filter(email=email).delete()
                    count+=1
                    
        return HttpResponse(["삭제 : " ,count])
    
    else : return redirect('login')
