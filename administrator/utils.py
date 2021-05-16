from django.utils import timezone


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
            return (available_seconds - usage_seconds)/available_seconds*100 
    else:
        return 0