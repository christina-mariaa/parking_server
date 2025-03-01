from django.db.models import Count, Sum
from datetime import datetime
from api.models import Booking, Payment, CustomUser, Car

def collect_statistics(start_date, end_date):
    return {
        "Общее количество бронирований": Booking.objects.filter(start_time__range=[start_date, end_date]).count(),
        "Бронирования по статусам": ", ".join(
            [f"{item['status']}: {item['count']}" for item in
             Booking.objects.filter(start_time__range=[start_date, end_date])
             .values('status')
             .annotate(count=Count('id'))]
        ),
        "Бронирования по тарифам": ", ".join(
            [f"{item['tariff__name']}: {item['count']}" for item in
             Booking.objects.filter(start_time__range=[start_date, end_date])
             .values('tariff__name')
             .annotate(count=Count('id'))]
        ),
        "Общая сумма оплат": Payment.objects.filter(payment_date__range=[start_date, end_date])
                                       .aggregate(total=Sum('amount'))['total'] or 0,
        "Новые пользователи": CustomUser.objects.filter(date_joined__range=[start_date, end_date]).count(),
        "Добавленные автомобили": Car.objects.filter(registered_at__range=[start_date, end_date]).count(),
    }


def collect_bookings(start_date, end_date):
    bookings = Booking.objects.filter(start_time__range=[start_date, end_date]).values(
        'id', 'start_time', 'end_time', 'car__license_plate', 'car__user__email', 'status', 'tariff__name',
        'parking_place__spot_number'
    )
    for booking in bookings:
        booking['start_time'] = booking['start_time'].replace(tzinfo=None)
        booking['end_time'] = booking['end_time'].replace(tzinfo=None)
    return bookings


def collect_payments(start_date, end_date):
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date]).values(
        'id', 'amount', 'payment_date', 'booking_id', 'booking__car__user__email'
    )
    for payment in payments:
        payment['payment_date'] = payment['payment_date'].replace(tzinfo=None)
    return payments


def collect_new_users(start_date, end_date):
    users = CustomUser.objects.filter(date_joined__range=[start_date, end_date]).values(
        'id', 'email', 'first_name', 'last_name', 'date_joined'
    )
    for user in users:
        user['date_joined'] = user['date_joined'].replace(tzinfo=None)
    return users


def collect_new_cars(start_date, end_date):
    cars = Car.objects.filter(registered_at__range=[start_date, end_date]).values(
        'id', 'user__email', 'license_plate', 'make', 'model', 'color', 'registered_at', 'is_deleted'
    )
    for car in cars:
        car['registered_at'] = car['registered_at'].replace(tzinfo=None)
    return cars
