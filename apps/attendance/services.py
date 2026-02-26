import datetime

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import AttendanceRecord, AttendanceLeave


# ── 출퇴근 서비스 ──────────────────────────────────────────────────
class AttendanceService:

    @staticmethod
    def check_in(employee):
        """출근 처리. 당일 중복 출근 시 오류."""
        today = timezone.localdate()
        if AttendanceRecord.objects.filter(employee=employee, work_date=today).exists():
            raise ValidationError('이미 오늘 출근 기록이 있습니다.')
        return AttendanceRecord.objects.create(
            employee=employee,
            work_date=today,
            check_in=timezone.now(),
        )

    @staticmethod
    def check_out(employee):
        """퇴근 처리. 출근 기록이 없거나 이미 퇴근한 경우 오류."""
        today = timezone.localdate()
        try:
            record = AttendanceRecord.objects.get(employee=employee, work_date=today)
        except AttendanceRecord.DoesNotExist:
            raise ValidationError('오늘 출근 기록이 없습니다.')

        if record.check_out:
            raise ValidationError('이미 퇴근 처리되었습니다.')

        now = timezone.now()
        record.check_out = now

        # 실근무시간 계산 (분 단위)
        delta = now - record.check_in
        total_minutes = int(delta.total_seconds() // 60)

        # 기본 근무시간: 8시간(480분), 초과분 산출
        standard = 480
        record.work_minutes     = total_minutes
        record.overtime_minutes = max(0, total_minutes - standard)
        record.save(update_fields=['check_out', 'work_minutes', 'overtime_minutes', 'updated_at'])
        return record

    @staticmethod
    def get_monthly_records(employee, year: int, month: int):
        return AttendanceRecord.objects.filter(
            employee=employee,
            work_date__year=year,
            work_date__month=month,
        ).order_by('work_date')


# ── 휴가 서비스 ────────────────────────────────────────────────────
class LeaveService:

    @staticmethod
    def request_leave(employee, validated_data: dict):
        """휴가 신청. 종료일이 시작일보다 앞서면 오류."""
        start = validated_data['start_date']
        end   = validated_data['end_date']
        if end < start:
            raise ValidationError('종료일은 시작일보다 이전일 수 없습니다.')
        return AttendanceLeave.objects.create(
            employee=employee,
            **validated_data,
        )

    @staticmethod
    def process_approval(leave: AttendanceLeave, action: str, approver, reject_reason: str = ''):
        """휴가 승인/반려. PENDING 상태만 처리 가능."""
        if leave.status != AttendanceLeave.Status.PENDING:
            raise ValidationError('이미 처리된 휴가 신청입니다.')

        from django.utils import timezone as tz
        if action == 'approve':
            leave.status      = AttendanceLeave.Status.APPROVED
            leave.approver    = approver
            leave.approved_at = tz.now()
            leave.save(update_fields=['status', 'approver', 'approved_at', 'updated_at'])
        else:
            leave.status        = AttendanceLeave.Status.REJECTED
            leave.approver      = approver
            leave.approved_at   = tz.now()
            leave.reject_reason = reject_reason
            leave.save(update_fields=['status', 'approver', 'approved_at', 'reject_reason', 'updated_at'])
        return leave
