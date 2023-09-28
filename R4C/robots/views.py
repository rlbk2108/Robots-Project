from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from robots.forms import RobotForm
from robots.models import Robot
from customers.models import Customer
from orders.models import Order
from openpyxl import Workbook
from datetime import datetime, timedelta
from django.db.models import Count
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


@csrf_exempt
def create_robot_instance(request):
    if request.method == 'POST':
        form = RobotForm(request.POST or None)

        if form.is_valid():
            form.save()


@csrf_exempt
def export_robots_data(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="robots.xlsx"'

    wb = Workbook()

    one_week = datetime.now() - timedelta(weeks=1)

    # получение отсортированного списка всех уникальных моделей за последнюю неделю
    all_models = (Robot.objects
                  .values_list('model', flat=True)
                  .distinct()
                  .order_by('model')
                  .filter(created__range=(one_week, datetime.now())))

    for i in range(0, len(all_models)):
        # создание нужного количества (кол-во моделей) страниц
        ws = wb.create_sheet('Model ' + all_models[i])
        ws.append(['Model', 'Version', 'Quantity'])

        # получение детализации определенной модели с ее версией и количеством
        robot = (Robot.objects
                 .values('model', 'version')
                 .annotate(entries=Count('model'))
                 .filter(model=all_models[i]))

        # запись данных в таблицу
        for item in robot:
            ws.append([item['model'], item['version'], item['entries']])

    wb.save(response)
    return response


def robot_exists_email(email, model, version):
    send_mail('Ваш заказ Робота.',
              'Доброго времени суток!\n'
              f'Робот модели {model}, версии {version} в наличии. '
              f'Пожалуйста, свяжитесь с нами.',
              'sanazera2@gmail.com',
              [email],
              fail_silently=False)


@csrf_exempt
def order_robot(request):
    if request.method == 'POST':
        email = request.user['email']
        serial = request.POST['robot_serial']
        model = serial[:2]
        version = serial[3:5]

        '''
        Проверка на наличие робота в системе
        Если робот имеется, создается соответсвующий объект модели и отправляется письмо клиенту
        В противном случае, создается тот же объект модели (Order) но письмо отправляется позже (когда робот появится)
        '''
        if Robot.objects.filter(model=model, version=version).exists():
            customer = Customer.objects.get(email=email)
            Order.objects.create(customer=customer, robot_serial=serial)
            robot_exists_email(email, model, version)
        else:
            customer = Customer.objects.get(email=email)
            Order.objects.create(customer=customer, robot_serial=serial)
