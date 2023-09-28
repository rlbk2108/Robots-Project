from django.urls import path

from robots import views

urlpatterns = [
    path('create_robot/', views.create_robot_instance)
]
