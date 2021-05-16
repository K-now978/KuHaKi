import json
from django.shortcuts import render, redirect
#from django.contrib.auth.models import User
from .models import Student
from .models import User
from seats.models import Seat, Reservation
from django.contrib import auth, messages

from django.contrib.auth import login as LOGIN
from django.contrib.auth import logout as LOGOUT
from django.conf import settings
from django.shortcuts import resolve_url
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.http import HttpResponse
from django.template.loader import render_to_string

import datetime


## 중복 코드
def get_rest_time(seat):
    if seat.booked:
        now = timezone.now()
        usage_seconds = (now - seat.booked.start_time).total_seconds()
        available_seconds = seat.booked.time

        start_time =seat.booked.start_time
        end_time = seat.booked.start_time + datetime.timedelta(seconds=available_seconds)
        

        if usage_seconds >= available_seconds:
            Reservation.remove_reservation(seat)
            return 0
        else:
            # percent of rest time.
            if (available_seconds - usage_seconds) <= 1800:
                extend_valid = True
            else:
                extend_valid = False
            return ((available_seconds - usage_seconds)/available_seconds*100), start_time.strftime('%H : %M %p'), end_time.strftime('%H : %M %p'), extend_valid
    else:
        return 0

def signup(request):
    def validate_password(password):
        validate_condition = [
            lambda s: any(x.islower() for x in s) or any(x.isupper() for x in s),
            lambda s: any(x.isdigit() for x in s),
            lambda s: len(s) == len(s.replace(" ","")),
            lambda s: len(s) >= 5
        ]
        for validator in validate_condition:
            if not validator(password):
                return True
    if request.method == 'POST':
        username = request.POST['username']
        student_id = request.POST['student_id']
        email = request.POST['email']
        
        context = {}
        context['email'] = email
        context['messages'] = []
        context['m_c'] = 0
        context['is_exist'] = 1
        if User.objects.filter(email=email).exists():
            context['messages'].append('이미 가입된 사용자입니다')
            context['m_c'] += 1
            context['is_exist'] = 0
            return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type = "application/json")
        if not Student.objects.filter(student_name=username, student_id=student_id, email=email).exists():
            context['m_c'] += 1
            context['is_exist'] = 0
            if not Student.objects.filter(student_name=username, student_id=student_id).exists():
                context['messages'].append('포탈 개인정보에 등록된 정보를 사용해 가입해야 합니다.')
                return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type = "application/json")
            else:
                context['messages'].append('신청하신 이메일과 다릅니다.')
        if validate_password(request.POST['password1']):
            context['messages'].append('비밀번호는 공백을 제외하고 영어와 숫자 조합으로 5자리 이상 입력하세요.')
            context['m_c'] += 1
            context['is_exist'] = 0
        if not request.POST['password1'] == request.POST['password2']:
            context['messages'].append('비밀번호가 다릅니다.')
            context['m_c'] += 1
            context['is_exist'] = 0
        if context['is_exist']:
            ## 메일 보내기
            student = Student.objects.get(student_name=username, student_id=student_id, email=email)
            auth_num = email_auth_num()
            student.auth = auth_num 
            student.save()
            send_mail(
                '[KuHaKi] 이메일 인증메일입니다.',
                [email],
                html=render_to_string('signup_email.html', {
                    'auth_num': auth_num,
                }),
            )
        print(json.dumps(context, cls=DjangoJSONEncoder))
        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type = "application/json")
    return render(request, 'signup.html')

def signup_auth_check(request):
    email = request.POST.get('email')
    input_auth_num = request.POST.get('input_auth_num')
    print(email)
    print(input_auth_num)
    student = Student.objects.get(email=email, auth=input_auth_num)
    student.auth = ""
    student.save()
    user = User.objects.create_user(
        student=student,
        email=email,
        password=request.POST.get('password')
    )
    messages.info(request, '가입 완료. 로그인 해주세요.')
    return HttpResponse(json.dumps({"email": user.email}, cls=DjangoJSONEncoder), content_type = "application/json")


def login(request):

    context = {}
    seats = Seat.objects.all()
    av_seats = 0
    not_covid = 0
    for seat in seats:
        if seat.available:
            not_covid += 1
            if seat.booked:
                now = timezone.now()
                reserve = seat.booked
                usage_seconds = (now - reserve.start_time).total_seconds()
                available_seconds = reserve.time

                if usage_seconds >= available_seconds:
                    Reservation.remove_reservation(seat)
                    av_seats += 1
            else:
                av_seats += 1
    context['total_seats'] = not_covid
    context['available_seats'] = av_seats

    if hasattr(request.user, 'reservation'): ## reservation 속성값이 있으면
        reserve = request.user.reservation
        my_seat = reserve.seat
        now = timezone.now()
        usage_seconds = (now - reserve.start_time).total_seconds()
        available_seconds = reserve.time

        if usage_seconds >= available_seconds:
            context['my_seat'] = None
            Reservation.remove_reservation(reserve)
        else:
            context['percent'], context['start_time'], context['end_time'], context['extend'] = get_rest_time(my_seat)
            tmp = dict()
            tmp['section'] = str(my_seat.section)
            tmp['number'] = my_seat.number
            context['my_seat'] = tmp
    else:
        context['my_seat'] = None


    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            if user.is_admin:
                return redirect('login')
            return redirect('seats')
        else:
            if User.objects.filter(email=email).exists():
                messages.info(request, '비밀번호를 확인해주세요.')
            else:
                messages.info(request, '이메일을 확인해주세요.')
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html', context)
    
def logout(request):
    auth.logout(request)
    return redirect('login')

def tips(request):
    return render(request, 'tips.html')

def kiosk(request):
    return render(request, 'kiosk.html')

def findpassword(request):
    return render(request, 'findpassword.html')

# Create your views here.


########################### 비밀번호 재설정

from django.views.generic import View
from .forms import RecoveryPwForm, CustomSetPasswordForm
from .utils import send_mail, email_auth_num

class RecoveryPwView(View):
    template_name = 'recovery_pw.html'
    recovery_pw = RecoveryPwForm

    def get(self, request):
        if request.method=='GET':
            form_pw = self.recovery_pw(None)
            return render(request, self.template_name, { 'form_pw':form_pw, })



# 비밀번호찾기 AJAX 통신
def ajax_find_pw_view(request):
    email = request.POST.get('email')
    result_pw = User.objects.get(email=email)
    if result_pw:
        auth_num = email_auth_num()
        result_pw.auth = auth_num 
        result_pw.save()
        send_mail(
            '[KuHaKi] 비밀번호 찾기 인증메일입니다.',
            [email],
            html=render_to_string('recovery_email.html', {
                'auth_num': auth_num,
            }),
        )

    # print(auth_num)
    return HttpResponse(json.dumps({"result": result_pw.email}, cls=DjangoJSONEncoder), content_type = "application/json")


# 비밀번호찾기 인증번호 확인
def auth_confirm_view(request):
    # if request.method=='POST' and 'auth_confirm' in request.POST:
    email = request.POST.get('email')
    input_auth_num = request.POST.get('input_auth_num')
    user = User.objects.get(email=email, auth=input_auth_num)
    user.auth = ""
    user.save()
    request.session['auth'] = user.email  
    
    return HttpResponse(json.dumps({"result": user.email}, cls=DjangoJSONEncoder), content_type = "application/json")
# 비밀번호찾기 새비밀번호 등록

def auth_pw_reset_view(request):
    if request.method == 'GET':
        if not request.session.get('auth', False):
            raise PermissionDenied

    if request.method == 'POST':
        session_user = request.session['auth']
        current_user = User.objects.get(email=session_user)
        # del(request.session['auth'])
        LOGIN(request, current_user)

        reset_password_form = CustomSetPasswordForm(request.user, request.POST)
        
        if reset_password_form.is_valid():
            user = reset_password_form.save()
            messages.success(request, "비밀번호 변경완료! 변경된 비밀번호로 로그인하세요.")
            LOGOUT(request)
            return redirect('login')
        else:
            LOGOUT(request)
            request.session['auth'] = session_user
    else:
        reset_password_form = CustomSetPasswordForm(request.user)

    return render(request, 'password_reset.html', {'form':reset_password_form})


def test(request):
    return render(request, 'test.html')