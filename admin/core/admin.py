# from django.contrib import admin
# from django_celery_beat.admin import \
#     ClockedScheduleAdmin as BaseClockedScheduleAdmin
# from django_celery_beat.admin import \
#     CrontabScheduleAdmin as BaseCrontabScheduleAdmin
# from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
# from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
# from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
#                                        IntervalSchedule, PeriodicTask,
#                                        SolarSchedule)
# from django_celery_results.admin import GroupResult, TaskResult
# from unfold.admin import ModelAdmin
# from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget
#
# admin.site.unregister(PeriodicTask)
# admin.site.unregister(IntervalSchedule)
# admin.site.unregister(CrontabSchedule)
# admin.site.unregister(SolarSchedule)
# admin.site.unregister(ClockedSchedule)
# admin.site.unregister(TaskResult)
# admin.site.unregister(GroupResult)
#
#
# class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
#     pass
#
#
# class UnfoldPeriodicTaskForm(PeriodicTaskForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["task"].widget = UnfoldAdminTextInputWidget()
#         self.fields["regtask"].widget = UnfoldTaskSelectWidget()
#
#
# @admin.register(TaskResult)
# class TaskResultAdmin(ModelAdmin):
#     # Отображаем нужные поля в списке
#     list_display = ('periodic_task_name', 'status', 'date_done', 'result', 'task_id')  # Добавляем result в отображаемые поля
#
#     # Можно также использовать fields, чтобы настроить, какие поля показывать на странице редактирования
#     readonly_fields = ['result', 'date_done']
#     fields = ('task_id', 'periodic_task_name', 'task_name', 'status', 'date_done', 'result', 'traceback')
#     search_fields = ['periodic_task_name', 'task_name', 'task_id']
#
#
# @admin.register(GroupResult)
# class GroupResultAdmin(ModelAdmin):
#     pass
#
#
# @admin.register(PeriodicTask)
# class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
#     form = UnfoldPeriodicTaskForm
#
#
# @admin.register(IntervalSchedule)
# class IntervalScheduleAdmin(ModelAdmin):
#     pass
#
#
# @admin.register(CrontabSchedule)
# class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
#     pass
#
#
# @admin.register(SolarSchedule)
# class SolarScheduleAdmin(ModelAdmin):
#     pass
#
#
# @admin.register(ClockedSchedule)
# class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
#     pass