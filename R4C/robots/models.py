from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from customers.models import Customer
from orders.models import Order
from django.core.mail import send_mail
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=False, null=False, auto_created=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)

    class Meta:
        unique_together = ('model', 'version')


@receiver(post_save, sender=Robot)
def robot_does_not_exists_email(sender, instance, **kwargs):

    # Фильтруем заказы по серийному номеру и проверяем на наличие почты клиента
    matching_orders = Order.objects.filter(
        robot_serial=instance.serial,
        customer__email__isnull=False
    )

    # Предполагается, что заказов на данного робота будет несколько, поэтому проходимся циклом
    for order in matching_orders:
        customer_email = order.customer.email

        # Отправляем письмо заданного в tasks.md формата
        send_mail('Ваш заказ Робота.',
                  f'Добрый день! Недавно вы интересовались нашим роботом модели {instance.model}, версии {instance.version}.\n'
                  'Этот робот теперь в наличии.\n'
                  'Если вам подходит этот вариант - пожалуйста, свяжитесь с нами',
                  'sanazera2@gmail.com',
                  [customer_email],
                  fail_silently=False)


# Валидация на соответствие существующего робота в системе (по примечание старшего технического специалиста)
@receiver(pre_save, sender=Robot)
def validate_model_exists(sender, instance, **kwargs):
    if not Robot.objects.filter(model=instance.model).exists():
        raise ValidationError(f"Model '{instance.model}' does not exist in the system.")


# Обновляем серийный номер скрещивая модель и версию
@receiver(pre_save, sender=Robot)
def update_serial(sender, instance, **kwargs):
    instance.serial = f'{instance.model}-{instance.version}'
