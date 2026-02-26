import re
from rest_framework import serializers

from apps.utils.encryption import decrypt, mask_resident_no
from .models import Department, Position, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['id', 'name', 'code', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Position
        fields = ['id', 'name', 'level', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """목록용: 급여·주민번호 제외, 부서/직급 nested"""
    department = DepartmentSerializer(read_only=True)
    position   = PositionSerializer(read_only=True)

    class Meta:
        model  = Employee
        fields = ['id', 'employee_no', 'name', 'department', 'position',
                  'hire_date', 'is_active']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """
    상세/입력용: 전체 필드.

    - 입력: department·position = FK ID (정수)
            resident_no = 평문 (990101-1234567)
    - 출력: department·position = nested object
            resident_no = 마스킹 (990101-*******)
    """
    resident_no = serializers.CharField(
        required=False, allow_blank=True, label='주민등록번호',
        help_text='입력: 평문 13자리 (YYMMDD-NNNNNNN). 조회 시 마스킹 반환.',
    )

    class Meta:
        model  = Employee
        fields = [
            'id', 'employee_no', 'name', 'resident_no',
            'department', 'position',
            'hire_date', 'resign_date', 'base_salary',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_active', 'resign_date', 'created_at', 'updated_at']
        extra_kwargs = {
            'department': {'queryset': Department.objects.filter(is_active=True)},
            'position':   {'queryset': Position.objects.filter(is_active=True)},
        }

    # ── 읽기 시 부서/직급 nested, 주민번호 마스킹 ─────────
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['department'] = DepartmentSerializer(instance.department).data
        data['position']   = PositionSerializer(instance.position).data
        data['resident_no'] = (
            mask_resident_no(decrypt(instance.resident_no))
            if instance.resident_no else ''
        )
        return data

    # ── 유효성 검사 ────────────────────────────────────────
    def validate_resident_no(self, value):
        if not value:
            return value
        clean = re.sub(r'[^0-9]', '', value)
        if len(clean) != 13:
            raise serializers.ValidationError(
                '주민등록번호는 13자리여야 합니다. (예: 990101-1234567)'
            )
        return value

    def validate_base_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError('기본급은 0보다 커야 합니다.')
        return value
