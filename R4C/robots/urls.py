from django.urls import path

from robots import views

urlpatterns = [
    path('create_robot/', views.create_robot_instance, name='create_robot'),
    path('export_robots_data/', views.export_robots_data, name="export_robots_data"),
    path('order_robot/', views.order_robot, name='order_robot'),
]
