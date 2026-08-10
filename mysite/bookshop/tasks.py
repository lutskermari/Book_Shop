from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from .models import Order


@shared_task
def send_order_email_async(order_id, recipient_email, total_cost):
    send_mail(
        subject=f"Замовлення #{order_id} успішно оплачено!",
        message=f"Дякуємо за замовлення! Сума до сплати: {total_cost} грн.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email],
    )


@shared_task
def generate_daily_sales_report():
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today, paid=True)
    total_sales = sum(order.get_total_cost() for order in today_orders)

    print(f"ЗВІТ ЗА {today}")
    print(f"Кількість замовлень: {today_orders.count()}")
    print(f"Загальна виручка: {total_sales} грн.")
    return f"Report generated for {today}: {total_sales} UAH"


@shared_task
def clear_expired_sessions():
    call_command("clearsessions")
    return "Expired sessions cleared successfully."
