from django.contrib import admin

from .models import PayrollRecord


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'year', 'month',
        'gross_pay', 'total_deduction', 'net_pay',
        'status', 'confirmed_at',
    ]
    list_filter  = ['status', 'year', 'month', 'employee__department']
    search_fields = ['employee__name', 'employee__employee_no']
    readonly_fields = [
        'gross_pay', 'total_deduction', 'net_pay',
        'national_pension', 'health_insurance', 'long_term_care',
        'employment_insurance', 'income_tax', 'local_income_tax',
        'confirmed_at', 'confirmed_by', 'created_at', 'updated_at',
    ]
