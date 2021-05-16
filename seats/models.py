from django.db import models
from django.conf import settings ## 이걸 왜하는지 모르겠음
from django.db import IntegrityError
from accounts.models import User


class Reservation(models.Model):
    # 좌석이 예약이 되어있는데 user를 삭제하려고할 때 오류 발생
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    start_time = models.DateTimeField()
    time = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'[{self.seat}] {self.user}'

    def remove_reservation(inst):
        if isinstance(inst, Reservation):
            inst.delete()
        elif isinstance(inst, Seat):
            if hasattr(inst, 'booked'):
                inst.booked.delete()
            else:
                raise Exception("This seat is not booked.")
        elif isinstance(inst, User):
            if hasattr(inst, 'reservation'):
                inst.reservation.delete()
            else:
                raise Exception("This user don't have a seat.")
        else:
            raise Exception('Input must be instance of User,Seat,Reservation.')
    
class Section(models.Model):
    name = models.CharField(unique=True,
                            max_length=2,
                            )
    
    def __str__(self):
        return self.name
    
    def make_section(section_name):
        if isinstance(section_name, tuple):
            for section in section_name:
                if not isinstance(section, str):
                    raise("tuple 속에는 string만 넣으세요")
                else:
                    tmp = Section(name=section)
                    tmp.save()

        elif isinstance(section_name, str):
            tmp = Section(name=section_name)
            tmp.save()

        else:
            raise("tuple 이나 string만 넣으세요")



class Seat(models.Model):
    section = models.ForeignKey("Section", on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    class Meta:
        unique_together = ('section', 'number',)
    booked = models.OneToOneField(Reservation,
                                    default=None, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    )

    # for COVID-19
    available = models.BooleanField(default=True)

    def __str__(self):
        if not self.available:
            return f'{self.section}-{self.number}[X]'
        return f'{self.section}-{self.number}'
    
    def make_seats(section_name, number_of_seats):
        section = Section.objects.filter(name=section_name)
        if len(section) == 0:
            raise("없는 Section입니다.")
        else:
            section = section[0]
        if not isinstance(number_of_seats, int):
            raise("좌석 갯수는 숫자만 넣으세요")
        
        fail = 0
        for i in range(1, number_of_seats+1):
            tmp = Seat(section=section, number=i)
            try:
                tmp.save()
            except IntegrityError as e: 
                if 'UNIQUE constraint' in e.args[0]:
                    fail += 1
        print(f"총 {number_of_seats-fail}개의 seats 생성 {fail}개는 이미 존재.")

    def _get_authnum(self):
        import json
        file_path = "./auth.json"
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
            authNum = json_data['authnum']
        print(authNum)

        

