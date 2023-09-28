from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


from robots.forms import RobotForm


@csrf_exempt
def create_robot_instance(request):
    if request.method == 'POST':
        form = RobotForm(request.POST or None)

        if form.is_valid():
            form.save()
