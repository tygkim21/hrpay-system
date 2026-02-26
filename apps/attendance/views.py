from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsEmployee, IsHRManager
from .models import AttendanceRecord, AttendanceLeave
from .serializers import (
    AttendanceRecordSerializer,
    AttendanceLeaveSerializer,
    LeaveApprovalSerializer,
)
from .services import AttendanceService, LeaveService


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


# ── 출근 ────────────────────────────────────────────────────────────
class CheckInView(APIView):
    """POST /api/v1/attendance/check-in/"""
    permission_classes = [IsEmployee]

    def post(self, request):
        user = request.user
        if not user.employee_id:
            return err('연결된 직원 정보가 없습니다.', status.HTTP_400_BAD_REQUEST)
        try:
            record = AttendanceService.check_in(user.employee)
        except Exception as e:
            return err(_extract_error(e))
        return ok(AttendanceRecordSerializer(record).data, '출근 처리되었습니다.', status.HTTP_201_CREATED)


# ── 퇴근 ────────────────────────────────────────────────────────────
class CheckOutView(APIView):
    """POST /api/v1/attendance/check-out/"""
    permission_classes = [IsEmployee]

    def post(self, request):
        user = request.user
        if not user.employee_id:
            return err('연결된 직원 정보가 없습니다.')
        try:
            record = AttendanceService.check_out(user.employee)
        except Exception as e:
            return err(_extract_error(e))
        return ok(AttendanceRecordSerializer(record).data, '퇴근 처리되었습니다.')


# ── 월별 근태 조회 ──────────────────────────────────────────────────
class MonthlyAttendanceView(APIView):
    """GET /api/v1/attendance/monthly/?year=2024&month=1"""
    permission_classes = [IsEmployee]

    def get(self, request):
        user = request.user
        if not user.employee_id:
            return err('연결된 직원 정보가 없습니다.')

        try:
            year  = int(request.query_params.get('year',  ''))
            month = int(request.query_params.get('month', ''))
        except (ValueError, TypeError):
            return err('year, month 파라미터를 정수로 입력해주세요.')

        records = AttendanceService.get_monthly_records(user.employee, year, month)
        return ok(AttendanceRecordSerializer(records, many=True).data)


# ── 휴가 목록 / 신청 ────────────────────────────────────────────────
class LeaveListCreateView(APIView):
    """
    GET  /api/v1/attendance/leaves/   — 본인 휴가 목록 (HR은 전체)
    POST /api/v1/attendance/leaves/   — 휴가 신청
    """
    permission_classes = [IsEmployee]

    def get(self, request):
        user = request.user
        if user.role in ('ADMIN', 'HR_MANAGER'):
            qs = AttendanceLeave.objects.select_related('employee', 'approver').all()
        else:
            if not user.employee_id:
                return ok([])
            qs = AttendanceLeave.objects.filter(employee=user.employee).select_related('approver')
        return ok(AttendanceLeaveSerializer(qs, many=True).data)

    def post(self, request):
        user = request.user
        if not user.employee_id:
            return err('연결된 직원 정보가 없습니다.')

        serializer = AttendanceLeaveSerializer(data=request.data)
        if not serializer.is_valid():
            msg = next(iter(serializer.errors.values()))[0]
            return err(str(msg))

        try:
            leave = LeaveService.request_leave(user.employee, serializer.validated_data)
        except Exception as e:
            return err(_extract_error(e))
        return ok(AttendanceLeaveSerializer(leave).data, '휴가 신청이 완료되었습니다.', status.HTTP_201_CREATED)


# ── 휴가 승인/반려 ──────────────────────────────────────────────────
class LeaveApprovalView(APIView):
    """POST /api/v1/attendance/leaves/<pk>/approve/"""
    permission_classes = [IsHRManager]

    def post(self, request, pk):
        leave = get_object_or_404(AttendanceLeave, pk=pk)
        serializer = LeaveApprovalSerializer(data=request.data)
        if not serializer.is_valid():
            msg = next(iter(serializer.errors.values()))[0]
            return err(str(msg))

        try:
            leave = LeaveService.process_approval(
                leave,
                action=serializer.validated_data['action'],
                approver=request.user,
                reject_reason=serializer.validated_data.get('reject_reason', ''),
            )
        except Exception as e:
            return err(_extract_error(e))

        action_label = '승인' if serializer.validated_data['action'] == 'approve' else '반려'
        return ok(AttendanceLeaveSerializer(leave).data, f'휴가 신청이 {action_label}되었습니다.')
