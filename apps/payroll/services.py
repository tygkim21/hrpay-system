from decimal import Decimal, ROUND_FLOOR

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.services import AttendanceService
from .models import PayrollRecord


# ── 공제율 상수 (2024 기준) ────────────────────────────────────────────
NATIONAL_PENSION_RATE     = Decimal('0.045')    # 4.5%
HEALTH_INSURANCE_RATE     = Decimal('0.03545')  # 3.545%
LONG_TERM_CARE_RATE       = Decimal('0.1281')   # 건강보험 × 12.81%
EMPLOYMENT_INSURANCE_RATE = Decimal('0.009')    # 0.9%
INCOME_TAX_RATE           = Decimal('0.02')     # 2.0% (간이세액 근사값)
LOCAL_INCOME_TAX_RATE     = Decimal('0.10')     # 소득세 × 10%

# ── 고정수당 ──────────────────────────────────────────────────────────
MEAL_ALLOWANCE      = Decimal('200000')
TRANSPORT_ALLOWANCE = Decimal('100000')

# ── 표준 월 근로시간 (초과근무수당 계산 기준) ───────────────────────────
STANDARD_MONTHLY_HOURS = Decimal('209')
OVERTIME_MULTIPLIER    = Decimal('1.5')


def _floor(amount: Decimal) -> Decimal:
    """원 단위 절사."""
    return amount.quantize(Decimal('1'), rounding=ROUND_FLOOR)


class PayrollService:

    @staticmethod
    def calculate(employee, year: int, month: int) -> PayrollRecord:
        """
        해당 직원의 year/month 급여를 계산하여 PayrollRecord(DRAFT)를 생성한다.
        이미 해당 월의 레코드가 존재하면 ValidationError.
        """
        if PayrollRecord.objects.filter(employee=employee, year=year, month=month).exists():
            raise ValidationError(f'{year}년 {month}월 급여가 이미 계산되었습니다.')

        # 기본급 스냅샷
        base_salary = Decimal(str(employee.base_salary))

        # 초과근무수당 계산
        records = AttendanceService.get_monthly_records(employee, year, month)
        total_overtime_minutes = sum(r.overtime_minutes for r in records)

        hourly_rate    = base_salary / STANDARD_MONTHLY_HOURS
        overtime_hours = Decimal(str(total_overtime_minutes)) / Decimal('60')
        overtime_pay   = _floor(hourly_rate * OVERTIME_MULTIPLIER * overtime_hours)

        # 총지급액
        gross_pay = base_salary + MEAL_ALLOWANCE + TRANSPORT_ALLOWANCE + overtime_pay

        # 공제 계산 (원 단위 절사)
        national_pension     = _floor(gross_pay * NATIONAL_PENSION_RATE)
        health_insurance     = _floor(gross_pay * HEALTH_INSURANCE_RATE)
        long_term_care       = _floor(health_insurance * LONG_TERM_CARE_RATE)
        employment_insurance = _floor(gross_pay * EMPLOYMENT_INSURANCE_RATE)
        income_tax           = _floor(gross_pay * INCOME_TAX_RATE)
        local_income_tax     = _floor(income_tax * LOCAL_INCOME_TAX_RATE)

        total_deduction = (
            national_pension + health_insurance + long_term_care
            + employment_insurance + income_tax + local_income_tax
        )
        net_pay = gross_pay - total_deduction

        return PayrollRecord.objects.create(
            employee             = employee,
            year                 = year,
            month                = month,
            base_salary          = base_salary,
            meal_allowance       = MEAL_ALLOWANCE,
            transport_allowance  = TRANSPORT_ALLOWANCE,
            overtime_pay         = overtime_pay,
            gross_pay            = gross_pay,
            national_pension     = national_pension,
            health_insurance     = health_insurance,
            long_term_care       = long_term_care,
            employment_insurance = employment_insurance,
            income_tax           = income_tax,
            local_income_tax     = local_income_tax,
            total_deduction      = total_deduction,
            net_pay              = net_pay,
            overtime_minutes     = total_overtime_minutes,
            status               = PayrollRecord.Status.DRAFT,
        )

    @staticmethod
    def confirm(record: PayrollRecord, confirmed_by) -> PayrollRecord:
        """
        DRAFT 급여를 CONFIRMED로 확정한다.
        이미 CONFIRMED 상태이면 ValidationError.
        """
        if record.status == PayrollRecord.Status.CONFIRMED:
            raise ValidationError('이미 확정된 급여입니다.')

        record.status       = PayrollRecord.Status.CONFIRMED
        record.confirmed_by = confirmed_by
        record.confirmed_at = timezone.now()
        record.save(update_fields=['status', 'confirmed_by', 'confirmed_at', 'updated_at'])
        return record
