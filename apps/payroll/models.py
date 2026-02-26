from django.conf import settings
from django.db import models

from apps.employees.models import Employee


class PayrollRecord(models.Model):

    class Status(models.TextChoices):
        DRAFT     = 'DRAFT',     '초안'
        CONFIRMED = 'CONFIRMED', '확정'

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name='직원',
        related_name='payroll_records',
    )
    year  = models.PositiveSmallIntegerField('급여연도')
    month = models.PositiveSmallIntegerField('급여월')

    # 지급항목
    base_salary         = models.DecimalField('기본급',     max_digits=15, decimal_places=2)
    meal_allowance      = models.DecimalField('식대',       max_digits=15, decimal_places=2, default=0)
    transport_allowance = models.DecimalField('교통비',     max_digits=15, decimal_places=2, default=0)
    overtime_pay        = models.DecimalField('초과근무수당', max_digits=15, decimal_places=2, default=0)
    gross_pay           = models.DecimalField('총지급액',   max_digits=15, decimal_places=2, default=0)

    # 공제항목
    national_pension      = models.DecimalField('국민연금',     max_digits=15, decimal_places=2, default=0)
    health_insurance      = models.DecimalField('건강보험',     max_digits=15, decimal_places=2, default=0)
    long_term_care        = models.DecimalField('장기요양보험',  max_digits=15, decimal_places=2, default=0)
    employment_insurance  = models.DecimalField('고용보험',     max_digits=15, decimal_places=2, default=0)
    income_tax            = models.DecimalField('소득세',       max_digits=15, decimal_places=2, default=0)
    local_income_tax      = models.DecimalField('지방소득세',   max_digits=15, decimal_places=2, default=0)
    total_deduction       = models.DecimalField('총공제액',     max_digits=15, decimal_places=2, default=0)

    net_pay = models.DecimalField('실수령액', max_digits=15, decimal_places=2, default=0)

    overtime_minutes = models.PositiveIntegerField('월 초과근무(분)', default=0)

    status       = models.CharField('상태', max_length=10, choices=Status.choices, default=Status.DRAFT)
    confirmed_at = models.DateTimeField('확정일시', null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='확정자',
        related_name='confirmed_payrolls',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'payroll_record'
        unique_together = ('employee', 'year', 'month')
        ordering        = ['-year', '-month', 'employee']

    def __str__(self):
        return f'[{self.employee}] {self.year}-{self.month:02d} ({self.get_status_display()})'
