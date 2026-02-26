from django.contrib import admin

from .models import AttendanceRecord, AttendanceLeave


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ('employee', 'work_date', 'check_in', 'check_out', 'work_minutes', 'overtime_minutes')
    list_filter   = ('work_date',)
    search_fields = ('employee__name', 'employee__employee_no')
    date_hierarchy = 'work_date'


@admin.register(AttendanceLeave)
class AttendanceLeaveAdmin(admin.ModelAdmin):
    list_display  = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'approver')
    list_filter   = ('status', 'leave_type')
    search_fields = ('employee__name', 'employee__employee_no')
