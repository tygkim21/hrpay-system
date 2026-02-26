"""
EmployeeService: 직원 생성·수정·퇴직 처리 비즈니스 로직.

- 주민번호 암호화/복호화는 이 레이어에서만 수행
- Serializer의 validated_data를 받아서 모델에 저장
"""
import datetime

from apps.utils.encryption import encrypt
from .models import Employee


class EmployeeService:

    @staticmethod
    def create(validated_data: dict) -> Employee:
        """직원 신규 등록. resident_no는 평문으로 받아 암호화 후 저장."""
        resident_no_plain = validated_data.pop('resident_no', '')
        employee = Employee(**validated_data)
        if resident_no_plain:
            employee.resident_no = encrypt(resident_no_plain)
        employee.save()
        return employee

    @staticmethod
    def update(instance: Employee, validated_data: dict) -> Employee:
        """직원 정보 수정. resident_no가 전달된 경우에만 재암호화."""
        resident_no_plain = validated_data.pop('resident_no', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if resident_no_plain is not None:
            instance.resident_no = encrypt(resident_no_plain) if resident_no_plain else ''
        instance.save()
        return instance

    @staticmethod
    def resign(instance: Employee, resign_date: datetime.date) -> Employee:
        """퇴직 처리: resign_date 기록 + is_active=False (소프트 삭제)."""
        instance.resign_date = resign_date
        instance.is_active   = False
        instance.save(update_fields=['resign_date', 'is_active', 'updated_at'])
        return instance
