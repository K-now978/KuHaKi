from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin)
# Create your models here.


# 보건과학대 학생 정보
class Student(models.Model):
    student_name = models.CharField(max_length=32,
                                    verbose_name="학생 이름"
                                    )
    email = models.EmailField(max_length=128,
                            verbose_name="학생 이메일"
                            )
    student_id = models.CharField(max_length=10,
                                verbose_name="학번"
                                )
    register_dttm = models.DateField(auto_now_add=True,
                                    verbose_name="기입날짜"
                                    )
    auth = models.CharField(max_length=8, default=None, null=True, blank=True)
    def __str__(self):
        return self.student_name
    
    # def add_students(students_list):


class MyUserManager(BaseUserManager):
    def create_user(self, student, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            student_info = student,
            email=MyUserManager.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        s = Student(student_name="superuser", email="000@korea.ac.kr", student_id=00000000)
        s.save()
        u = self.create_user(student=s,
                             email=email,
                             password=password,
                             )
        u.is_admin = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser,  PermissionsMixin):

    student_info = models.OneToOneField(Student, on_delete=models.CASCADE)

    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )

    auth = models.CharField(max_length=8, default=None, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return f'{self.student_info}'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

