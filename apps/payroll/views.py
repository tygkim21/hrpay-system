from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from itertools import groupby

from django.utils import timezone

from apps.accounts.permissions import IsAdmin, IsHRManager, IsEmployee, IsOwnerOrHRManager
from .models import PayrollRecord
from .serializers import PayrollRecordSerializer, LedgerRecordSerializer
from .services import PayrollService


def ok(data, message='', status_code=status.HTTP_200_OK):
    return Response({'success': True, 'data': data, 'message': message}, status=status_code)


def err(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'data': None, 'message': message}, status=status_code)


def _extract_error(exc) -> str:
    """DRF ValidationError의 detail에서 첫 번째 오류 메시지를 문자열로 반환."""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    if isinstance(exc, DRFValidationError):
        detail = exc.detail
        if isinstance(detail, list):
            return str(detail[0])
        if isinstance(detail, dict):
            first_val = next(iter(detail.values()))
            return str(first_val[0] if isinstance(first_val, list) else first_val)
        return str(detail)
    return str(exc)


# ── 급여 계산 ────────────────────────────────────────────────────────
class CalculatePayrollView(APIView):
    """POST /api/v1/payroll/calculate/"""
    permission_classes = [IsHRManager]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        year        = request.data.get('year')
        month       = request.data.get('month')

        if not all([employee_id, year, month]):
            return err('employee_id, year, month 값이 필요합니다.')

        try:
            year  = int(year)
            month = int(month)
        except (TypeError, ValueError):
            return err('year, month는 정수여야 합니다.')

        if not (1 <= month <= 12):
            return err('month는 1~12 사이여야 합니다.')

        from apps.employees.models import Employee
        employee = get_object_or_404(Employee, pk=employee_id, is_active=True)

        try:
            record = PayrollService.calculate(employee, year, month)
        except Exception as e:
            return err(_extract_error(e))

        return ok(
            PayrollRecordSerializer(record).data,
            f'{year}년 {month}월 급여가 계산되었습니다.',
            status.HTTP_201_CREATED,
        )


# ── 급여 목록 ────────────────────────────────────────────────────────
class PayrollListView(APIView):
    """GET /api/v1/payroll/?year=2024&month=1"""
    permission_classes = [IsHRManager]

    def get(self, request):
        qs = PayrollRecord.objects.select_related(
            'employee', 'employee__department', 'confirmed_by'
        ).all()

        year  = request.query_params.get('year')
        month = request.query_params.get('month')
        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)

        return ok(PayrollRecordSerializer(qs, many=True).data)


# ── 급여 상세 ────────────────────────────────────────────────────────
class PayrollDetailView(APIView):
    """GET /api/v1/payroll/<id>/"""
    permission_classes = [IsEmployee]

    def get(self, request, pk):
        record = get_object_or_404(
            PayrollRecord.objects.select_related(
                'employee', 'employee__department', 'confirmed_by'
            ),
            pk=pk,
        )
        # HR/Admin은 모두 조회, 일반 직원은 본인 것만
        if request.user.role not in ('ADMIN', 'HR_MANAGER'):
            if not (request.user.employee_id and
                    record.employee_id == request.user.employee_id):
                return Response(
                    {'success': False, 'data': None, 'message': '접근 권한이 없습니다.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return ok(PayrollRecordSerializer(record).data)


# ── 급여 확정 ────────────────────────────────────────────────────────
class ConfirmPayrollView(APIView):
    """POST /api/v1/payroll/<id>/confirm/"""
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        record = get_object_or_404(PayrollRecord, pk=pk)
        try:
            record = PayrollService.confirm(record, confirmed_by=request.user)
        except Exception as e:
            return err(_extract_error(e))
        return ok(PayrollRecordSerializer(record).data, '급여가 확정되었습니다.')


# ── 내 급여 목록 ─────────────────────────────────────────────────────
class MyPayrollView(APIView):
    """GET /api/v1/payroll/my/"""
    permission_classes = [IsEmployee]

    def get(self, request):
        if not request.user.employee_id:
            return ok([])
        qs = PayrollRecord.objects.filter(
            employee_id=request.user.employee_id
        ).select_related('employee', 'employee__department', 'confirmed_by').order_by('-year', '-month')
        return ok(PayrollRecordSerializer(qs, many=True).data)


# ── 급여대장 (리포트) ──────────────────────────────────────────────────
class PayrollLedgerView(APIView):
    """GET /api/v1/payroll/reports/ledger/?year=2024&month=1

    부서별로 그룹화된 급여대장 데이터를 반환한다.
    각 부서 소계와 전체 합계를 포함한다.
    """
    permission_classes = [IsHRManager]

    def get(self, request):
        year  = request.query_params.get('year')
        month = request.query_params.get('month')

        if not year or not month:
            return err('year, month 파라미터가 필요합니다.')

        try:
            year  = int(year)
            month = int(month)
        except (TypeError, ValueError):
            return err('year, month는 정수여야 합니다.')

        if not (1 <= month <= 12):
            return err('month는 1~12 사이여야 합니다.')

        records = list(
            PayrollRecord.objects.filter(year=year, month=month)
            .select_related(
                'employee',
                'employee__department',
                'employee__position',
            )
            .order_by('employee__department__name', 'employee__employee_no')
        )

        # 부서별 그룹화 및 소계 계산
        departments = []
        for dept_name, group in groupby(records, key=lambda r: r.employee.department.name):
            dept_records = list(group)
            departments.append({
                'name':               dept_name,
                'count':              len(dept_records),
                'subtotal_gross_pay': str(sum(r.gross_pay       for r in dept_records)),
                'subtotal_deduction': str(sum(r.total_deduction for r in dept_records)),
                'subtotal_net_pay':   str(sum(r.net_pay         for r in dept_records)),
                'records':            LedgerRecordSerializer(dept_records, many=True).data,
            })

        data = {
            'year':            year,
            'month':           month,
            'generated_at':    timezone.now().isoformat(),
            'total_count':     len(records),
            'total_gross_pay': str(sum(r.gross_pay       for r in records)),
            'total_deduction': str(sum(r.total_deduction for r in records)),
            'total_net_pay':   str(sum(r.net_pay         for r in records)),
            'departments':     departments,
        }
        return ok(data)
