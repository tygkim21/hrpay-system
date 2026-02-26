import datetime
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.employees.models import Department, Position, Employee
from apps.utils.encryption import encrypt
from .models import AttendanceRecord, AttendanceLeave

User = get_user_model()

CHECK_IN_URL  = '/api/v1/attendance/check-in/'
CHECK_OUT_URL = '/api/v1/attendance/check-out/'
MONTHLY_URL   = '/api/v1/attendance/monthly/'
LEAVES_URL    = '/api/v1/attendance/leaves/'


# ── 공통 헬퍼 ────────────────────────────────────────────────────
def make_dept(name='개발팀', code='DEV'):
    return Department.objects.create(name=name, code=code)

def make_pos(name='사원', level=1):
    return Position.objects.create(name=name, level=level)

def make_employee(dept, pos, employee_no='EMP001', name='홍길동'):
    return Employee.objects.create(
        employee_no=employee_no,
        name=name,
        resident_no=encrypt('990101-1234567'),
        department=dept,
        position=pos,
        hire_date=datetime.date(2024, 1, 1),
        base_salary='3000000',
    )

def make_user(username, password='pass1234', role='EMPLOYEE', employee=None):
    user = User.objects.create_user(username=username, password=password, role=role)
    if employee:
        user.employee = employee
        user.save()
    return user

def get_token(client, username, password='pass1234'):
    res = client.post('/api/v1/auth/login/', {'username': username, 'password': password})
    return res.data['data']['access']

def auth(client, token):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


# ── 출퇴근 테스트 ────────────────────────────────────────────────
class CheckInOutTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj  = make_employee(dept, pos, 'EMP001', '홍길동')
        self.user     = make_user('emp1', role='EMPLOYEE', employee=self.emp_obj)
        self.no_emp_user = make_user('nolink', role='EMPLOYEE')  # employee 미연결
        auth(self.client, get_token(self.client, 'emp1'))

    def test_check_in_success(self):
        res = self.client.post(CHECK_IN_URL)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        self.assertIsNotNone(res.data['data']['check_in'])
        self.assertIsNone(res.data['data']['check_out'])

    def test_check_in_duplicate_fails(self):
        self.client.post(CHECK_IN_URL)
        res = self.client.post(CHECK_IN_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_check_in_no_employee_link_fails(self):
        auth(self.client, get_token(self.client, 'nolink'))
        res = self.client.post(CHECK_IN_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_out_success(self):
        self.client.post(CHECK_IN_URL)
        res = self.client.post(CHECK_OUT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertIsNotNone(res.data['data']['check_out'])
        self.assertGreaterEqual(res.data['data']['work_minutes'], 0)

    def test_check_out_without_check_in_fails(self):
        res = self.client.post(CHECK_OUT_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_check_out_twice_fails(self):
        self.client.post(CHECK_IN_URL)
        self.client.post(CHECK_OUT_URL)
        res = self.client.post(CHECK_OUT_URL)
        self.assertFalse(res.data['success'])

    def test_overtime_calculated_correctly(self):
        """9시간 근무 시 overtime_minutes = 60 (540 - 480)"""
        now = timezone.now()
        past = now - datetime.timedelta(hours=9)
        AttendanceRecord.objects.create(
            employee=self.emp_obj,
            work_date=timezone.localdate(),
            check_in=past,
        )
        res = self.client.post(CHECK_OUT_URL)
        self.assertTrue(res.data['success'])
        self.assertGreaterEqual(res.data['data']['overtime_minutes'], 55)  # 약 60분 초과

    def test_unauthenticated_fails(self):
        self.client.credentials()
        res = self.client.post(CHECK_IN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 월별 조회 테스트 ─────────────────────────────────────────────
class MonthlyAttendanceTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj = make_employee(dept, pos)
        self.user    = make_user('emp2', role='EMPLOYEE', employee=self.emp_obj)
        auth(self.client, get_token(self.client, 'emp2'))

        # 2024년 1월 기록 2개
        AttendanceRecord.objects.create(employee=self.emp_obj, work_date=datetime.date(2024, 1, 2))
        AttendanceRecord.objects.create(employee=self.emp_obj, work_date=datetime.date(2024, 1, 3))

    def test_monthly_returns_correct_records(self):
        res = self.client.get(MONTHLY_URL, {'year': 2024, 'month': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 2)

    def test_monthly_empty_for_other_month(self):
        res = self.client.get(MONTHLY_URL, {'year': 2024, 'month': 2})
        self.assertEqual(len(res.data['data']), 0)

    def test_monthly_invalid_params_fails(self):
        res = self.client.get(MONTHLY_URL, {'year': 'abc', 'month': 1})
        self.assertFalse(res.data['success'])


# ── 휴가 신청 테스트 ─────────────────────────────────────────────
class LeaveTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj = make_employee(dept, pos)
        self.emp_user = make_user('emp3', role='EMPLOYEE', employee=self.emp_obj)
        self.hr_user  = make_user('hr1', role='HR_MANAGER')
        auth(self.client, get_token(self.client, 'emp3'))

        self.leave_data = {
            'leave_type': 'ANNUAL',
            'start_date': '2024-06-01',
            'end_date':   '2024-06-02',
            'reason':     '개인 사유',
        }

    def test_request_leave_success(self):
        res = self.client.post(LEAVES_URL, self.leave_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['status'], 'PENDING')

    def test_request_leave_end_before_start_fails(self):
        data = {**self.leave_data, 'start_date': '2024-06-05', 'end_date': '2024-06-01'}
        res  = self.client.post(LEAVES_URL, data)
        self.assertFalse(res.data['success'])

    def test_list_own_leaves(self):
        AttendanceLeave.objects.create(
            employee=self.emp_obj,
            leave_type='ANNUAL',
            start_date=datetime.date(2024, 6, 1),
            end_date=datetime.date(2024, 6, 2),
        )
        res = self.client.get(LEAVES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 1)

    def test_hr_sees_all_leaves(self):
        AttendanceLeave.objects.create(
            employee=self.emp_obj,
            leave_type='ANNUAL',
            start_date=datetime.date(2024, 6, 1),
            end_date=datetime.date(2024, 6, 2),
        )
        auth(self.client, get_token(self.client, 'hr1'))
        res = self.client.get(LEAVES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 1)

    def test_unauthenticated_cannot_request(self):
        self.client.credentials()
        res = self.client.post(LEAVES_URL, self.leave_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 휴가 승인/반려 테스트 ────────────────────────────────────────
class LeaveApprovalTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj  = make_employee(dept, pos)
        self.emp_user = make_user('emp4', role='EMPLOYEE', employee=self.emp_obj)
        self.hr_user  = make_user('hr2', role='HR_MANAGER')
        auth(self.client, get_token(self.client, 'hr2'))

        self.leave = AttendanceLeave.objects.create(
            employee=self.emp_obj,
            leave_type='ANNUAL',
            start_date=datetime.date(2024, 7, 1),
            end_date=datetime.date(2024, 7, 2),
        )

    def _url(self):
        return f'{LEAVES_URL}{self.leave.id}/approve/'

    def test_approve_success(self):
        res = self.client.post(self._url(), {'action': 'approve'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['status'], 'APPROVED')

    def test_reject_success(self):
        res = self.client.post(self._url(), {'action': 'reject', 'reject_reason': '일정 충돌'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['status'], 'REJECTED')

    def test_reject_without_reason_fails(self):
        res = self.client.post(self._url(), {'action': 'reject'})
        self.assertFalse(res.data['success'])

    def test_approve_already_processed_fails(self):
        self.client.post(self._url(), {'action': 'approve'})
        res = self.client.post(self._url(), {'action': 'approve'})
        self.assertFalse(res.data['success'])

    def test_employee_cannot_approve(self):
        auth(self.client, get_token(self.client, 'emp4'))
        res = self.client.post(self._url(), {'action': 'approve'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_action_fails(self):
        res = self.client.post(self._url(), {'action': 'invalid'})
        self.assertFalse(res.data['success'])
