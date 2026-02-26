from rest_framework import serializers

from .models import PayrollRecord


class LedgerRecordSerializer(serializers.ModelSerializer):
    """급여대장용 — 사번·직급 포함, 상태 표시 포함."""
    employee_no   = serializers.CharField(source='employee.employee_no', read_only=True)
    employee_name = serializers.CharField(source='employee.name',        read_only=True)
    position_name = serializers.CharField(source='employee.position.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = PayrollRecord
        fields = [
            'id', 'employee_no', 'employee_name', 'position_name',
            'base_salary', 'meal_allowance', 'transport_allowance',
            'overtime_pay', 'gross_pay',
            'national_pension', 'health_insurance', 'long_term_care',
            'employment_insurance', 'income_tax', 'local_income_tax',
            'total_deduction', 'net_pay',
            'overtime_minutes', 'status', 'status_display',
        ]
        read_only_fields = fields


class PayrollRecordSerializer(serializers.ModelSerializer):
    status_display    = serializers.CharField(source='get_status_display', read_only=True)
    employee_name     = serializers.CharField(source='employee.name', read_only=True)
    department_name   = serializers.CharField(source='employee.department.name', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.get_full_name', read_only=True, default=None)

    class Meta:
        model  = PayrollRecord
        fields = [
            'id', 'employee', 'employee_name', 'department_name',
            'year', 'month',
            # 지급항목
            'base_salary', 'meal_allowance', 'transport_allowance',
            'overtime_pay', 'gross_pay',
            # 공제항목
            'national_pension', 'health_insurance', 'long_term_care',
            'employment_insurance', 'income_tax', 'local_income_tax',
            'total_deduction',
            # 실수령액
            'net_pay',
            'overtime_minutes',
            # 상태
            'status', 'status_display',
            'confirmed_at', 'confirmed_by', 'confirmed_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'employee', 'employee_name', 'department_name',
            'year', 'month',
            'base_salary', 'meal_allowance', 'transport_allowance',
            'overtime_pay', 'gross_pay',
            'national_pension', 'health_insurance', 'long_term_care',
            'employment_insurance', 'income_tax', 'local_income_tax',
            'total_deduction', 'net_pay', 'overtime_minutes',
            'status', 'status_display',
            'confirmed_at', 'confirmed_by', 'confirmed_by_name',
            'created_at', 'updated_at',
        ]
