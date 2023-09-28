from django.contrib import admin
from robots.models import Robot
from import_export.admin import ExportActionMixin


class RobotAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('model', 'version')


admin.site.register(Robot, RobotAdmin)
