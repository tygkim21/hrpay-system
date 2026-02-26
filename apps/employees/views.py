import datetime

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsAdmin, IsHRManager
from .models import Department, Position, Employee
from .serializers import (
    DepartmentSerializer, PositionSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer,
)
from .services import EmployeeService


# ── 응답 헬퍼 ────────────────────────────────────────────────────
def ok(data=None, msg='', code=status.HTTP_200_OK):
    return Response({'success': True,  'data': data, 'message': msg}, status=code)

def err(msg='', code=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'data': None, 'message': msg}, status=code)


# ── 부서 ─────────────────────────────────────────────────────────
class DepartmentListView(APIView):
    permission_classes = [IsHRManager]

    def get(self, request):
        qs = Department.objects.filter(is_active=True)
        return ok(data=DepartmentSerializer(qs, many=True).data)

    def post(self, request):
        s = DepartmentSerializer(data=request.data)
        if not s.is_valid():
            return err(s.errors)
        s.save()
        return ok(data=s.data, msg='부서가 등록되었습니다.', code=status.HTTP_201_CREATED)


# ── 직급 ─────────────────────────────────────────────────────────
class PositionListView(APIView):
    permission_classes = [IsHRManager]

    def get(self, request):
        qs = Position.objects.filter(is_active=True)
        return ok(data=PositionSerializer(qs, many=True).data)

    def post(self, request):
        s = PositionSerializer(data=request.data)
        if not s.is_valid():
            return err(s.errors)
        s.save()
        return ok(data=s.data, msg='직급이 등록되었습니다.', code=status.HTTP_201_CREATED)


# ── 직원 목록 / 등록 ─────────────────────────────────────────────
class EmployeeListView(APIView):
    permission_classes = [IsHRManager]

    def get(self, request):
        qs = Employee.objects.select_related('department', 'position').order_by('employee_no')

        search    = request.query_params.get('search', '').strip()
        dept_id   = request.query_params.get('department', '').strip()
        is_active = request.query_params.get('is_active', '').strip()

        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(employee_no__icontains=search)
            )
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        if is_active:
            qs = qs.filter(is_active=(is_active.lower() == 'true'))

        return ok(data=EmployeeListSerializer(qs, many=True).data)

    def post(self, request):
        s = EmployeeDetailSerializer(data=request.data)
        if not s.is_valid():
            return err(s.errors)
        employee = EmployeeService.create(s.validated_data)
        return ok(
            data=EmployeeDetailSerializer(employee).data,
            msg='직원이 등록되었습니다.',
            code=status.HTTP_201_CREATED,
        )


# ── 직원 상세 / 수정 ─────────────────────────────────────────────
class EmployeeDetailView(APIView):
    permission_classes = [IsHRManager]

    def _get_or_404(self, pk):
        try:
            return Employee.objects.select_related('department', 'position').get(pk=pk)
        except Employee.DoesNotExist:
            return None

    def get(self, request, pk):
        employee = self._get_or_404(pk)
        if not employee:
            return err('직원을 찾을 수 없습니다.', status.HTTP_404_NOT_FOUND)
        return ok(data=EmployeeDetailSerializer(employee).data)

    def put(self, request, pk):
        employee = self._get_or_404(pk)
        if not employee:
            return err('직원을 찾을 수 없습니다.', status.HTTP_404_NOT_FOUND)
        s = EmployeeDetailSerializer(employee, data=request.data, partial=True)
        if not s.is_valid():
            return err(s.errors)
        updated = EmployeeService.update(employee, s.validated_data)
        return ok(data=EmployeeDetailSerializer(updated).data, msg='직원 정보가 수정되었습니다.')


# ── 퇴직 처리 ────────────────────────────────────────────────────
class EmployeeResignView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return err('직원을 찾을 수 없습니다.', status.HTTP_404_NOT_FOUND)

        if not employee.is_active:
            return err('이미 퇴직 처리된 직원입니다.')

        resign_date_str = request.data.get('resign_date')
        if not resign_date_str:
            return err('퇴직일(resign_date)을 입력해주세요.')

        try:
            resign_date = datetime.date.fromisoformat(str(resign_date_str))
        except ValueError:
            return err('퇴직일 형식이 올바르지 않습니다. (YYYY-MM-DD)')

        if resign_date < employee.hire_date:
            return err('퇴직일은 입사일보다 이후여야 합니다.')

        updated = EmployeeService.resign(employee, resign_date)
        return ok(
            data=EmployeeDetailSerializer(updated).data,
            msg=f'{employee.name} 직원의 퇴직 처리가 완료되었습니다.',
        )
