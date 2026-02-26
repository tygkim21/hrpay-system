# apps/accounts/permissions.py

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """시스템 관리자만 접근 가능"""
    message = '시스템 관리자 권한이 필요합니다.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsHRManager(BasePermission):
    """인사담당자 이상 접근 가능 (관리자 포함)"""
    message = '인사/급여 담당자 이상의 권한이 필요합니다.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ('ADMIN', 'HR_MANAGER')
        )


class IsEmployee(BasePermission):
    """로그인한 모든 직원 접근 가능"""
    message = '로그인이 필요합니다.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwnerOrHRManager(BasePermission):
    """본인 데이터이거나 인사담당자 이상"""
    message = '본인 또는 인사담당자 이상의 권한이 필요합니다.'

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('ADMIN', 'HR_MANAGER'):
            return True
        # obj가 직원 본인인지 확인
        return hasattr(obj, 'user') and obj.user == request.user
