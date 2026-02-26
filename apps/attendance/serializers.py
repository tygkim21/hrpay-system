from rest_framework import serializers

from .models import AttendanceRecord, AttendanceLeave


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_no   = serializers.CharField(source='employee.employee_no', read_only=True)

    class Meta:
        model  = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_no',
            'work_date', 'check_in', 'check_out',
            'work_minutes', 'overtime_minutes',
        ]
        read_only_fields = ['work_minutes', 'overtime_minutes']


class AttendanceLeaveSerializer(serializers.ModelSerializer):
    employee_name   = serializers.CharField(source='employee.name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display     = serializers.CharField(source='get_status_display', read_only=True)
    approver_username  = serializers.CharField(source='approver.username', read_only=True, default=None)

    class Meta:
        model  = AttendanceLeave
        fields = [
            'id', 'employee', 'employee_name',
            'leave_type', 'leave_type_display',
            'start_date', 'end_date', 'reason',
            'status', 'status_display',
            'approver', 'approver_username', 'approved_at', 'reject_reason',
            'created_at',
        ]
        read_only_fields = ['employee', 'status', 'approver', 'approved_at', 'reject_reason']


class LeaveApprovalSerializer(serializers.Serializer):
    action        = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('reject_reason', '').strip():
            raise serializers.ValidationError({'reject_reason': '반려 사유를 입력해주세요.'})
        return data
