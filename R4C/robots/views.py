from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from robots.forms import RobotForm
from robots.models import Robot
from openpyxl import Workbook
from datetime import datetime, timedelta
from django.db.models import Count


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
