  
from django import forms
from django.contrib.auth.hashers import check_password
from .models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

class RecoveryPwForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput,
    )
    class Meta:
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(RecoveryPwForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs.update({
            # 'placeholder': '이메일을 입력해주세요',
            'class': 'form-control',
            'id': 'pw_form_email',
        })

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'new password'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '새 비밀번호',
        })
        self.fields['new_password2'].label = 'new password(confirm)'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '새 비밀번호 확인',
        })