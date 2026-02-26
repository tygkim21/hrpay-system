import datetime
from decimal import Decimal

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.employees.models import Department, Position, Employee
from apps.utils.encryption import encrypt
from apps.attendance.models import AttendanceRecord
from .models import PayrollRecord

User = get_user_model()

CALCULATE_URL = '/api/v1/payroll/calculate/'
LIST_URL      = '/api/v1/payroll/'
MY_URL        = '/api/v1/payroll/my/'
LEDGER_URL    = '/api/v1/payroll/reports/ledger/'


# ── 공통 헬퍼 ────────────────────────────────────────────────────────
def make_dept(name='개발팀', code='DEV'):
    return Department.objects.create(name=name, code=code)


def make_pos(name='사원', level=1):
    return Position.objects.create(name=name, level=level)


def make_employee(dept, pos, employee_no='EMP001', name='홍길동', base_salary='3000000'):
    return Employee.objects.create(
        employee_no=employee_no,
        name=name,
        resident_no=encrypt('990101-1234567'),
        department=dept,
        position=pos,
        hire_date=datetime.date(2024, 1, 1),
        base_salary=base_salary,
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


def detail_url(pk):
    return f'/api/v1/payroll/{pk}/'


def confirm_url(pk):
    return f'/api/v1/payroll/{pk}/confirm/'


# ── 급여 계산 테스트 ─────────────────────────────────────────────────
class PayrollCalculateTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj  = make_employee(dept, pos, 'EMP001', '홍길동', '3000000')
        self.hr_user  = make_user('hr1', role='HR_MANAGER')
        self.emp_user = make_user('emp1', role='EMPLOYEE', employee=self.emp_obj)
        self.admin    = make_user('admin1', role='ADMIN')
        auth(self.client, get_token(self.client, 'hr1'))

    def _post(self, year=2024, month=1, employee_id=None):
        if employee_id is None:
            employee_id = self.emp_obj.id
        return self.client.post(CALCULATE_URL, {
            'employee_id': employee_id,
            'year':        year,
            'month':       month,
        })

    def test_calculate_success(self):
        res = self._post()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        data = res.data['data']
        self.assertEqual(data['year'],  2024)
        self.assertEqual(data['month'], 1)
        self.assertEqual(data['status'], 'DRAFT')
        # 기본급 스냅샷 확인
        self.assertEqual(Decimal(data['base_salary']), Decimal('3000000'))
        # 고정수당 확인
        self.assertEqual(Decimal(data['meal_allowance']),      Decimal('200000'))
        self.assertEqual(Decimal(data['transport_allowance']), Decimal('100000'))
        # 총지급액 = 기본급 + 식대 + 교통비 (초과 없음)
        self.assertEqual(Decimal(data['gross_pay']), Decimal('3300000'))
        # 실수령액 > 0
        self.assertGreater(Decimal(data['net_pay']), 0)

    def test_calculate_duplicate_fails(self):
        self._post()
        res = self._post()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_calculate_with_overtime(self):
        """초과근무 60분이 있을 때 overtime_pay > 0"""
        AttendanceRecord.objects.create(
            employee=self.emp_obj,
            work_date=datetime.date(2024, 1, 15),
            overtime_minutes=60,
        )
        res = self._post(year=2024, month=1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.data['data']
        self.assertEqual(data['overtime_minutes'], 60)
        ot_pay = Decimal(data['overtime_pay'])
        # 시간당 기본급 = 3000000 / 209 ≈ 14354.07, × 1.5 × 1h ≈ 21531
        self.assertGreater(ot_pay, 0)

    def test_calculate_requires_hr_permission(self):
        auth(self.client, get_token(self.client, 'emp1'))
        res = self._post()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_calculate_invalid_month_fails(self):
        res = self._post(month=13)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_missing_params_fails(self):
        res = self.client.post(CALCULATE_URL, {'year': 2024})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])


# ── 급여 목록 테스트 ─────────────────────────────────────────────────
class PayrollListTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj  = make_employee(dept, pos)
        self.hr_user  = make_user('hr2', role='HR_MANAGER')
        self.emp_user = make_user('emp2', role='EMPLOYEE', employee=self.emp_obj)
        auth(self.client, get_token(self.client, 'hr2'))

        # 레코드 2개 생성 (직접 DB 삽입)
        PayrollRecord.objects.create(
            employee=self.emp_obj, year=2024, month=1,
            base_salary='3000000', gross_pay='3300000',
            total_deduction='300000', net_pay='3000000',
        )
        PayrollRecord.objects.create(
            employee=self.emp_obj, year=2024, month=2,
            base_salary='3000000', gross_pay='3300000',
            total_deduction='300000', net_pay='3000000',
        )

    def test_list_returns_all_records(self):
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 2)

    def test_filter_by_year_and_month(self):
        res = self.client.get(LIST_URL, {'year': 2024, 'month': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 1)
        self.assertEqual(res.data['data'][0]['month'], 1)

    def test_employee_cannot_access_list(self):
        auth(self.client, get_token(self.client, 'emp2'))
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_list(self):
        self.client.credentials()
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 급여 상세 테스트 ─────────────────────────────────────────────────
class PayrollDetailTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj   = make_employee(dept, pos, 'EMP001', '홍길동')
        self.emp_obj2  = make_employee(dept, pos, 'EMP002', '김철수')
        self.hr_user   = make_user('hr3', role='HR_MANAGER')
        self.emp_user  = make_user('emp3', role='EMPLOYEE', employee=self.emp_obj)
        self.emp_user2 = make_user('emp4', role='EMPLOYEE', employee=self.emp_obj2)

        self.record = PayrollRecord.objects.create(
            employee=self.emp_obj, year=2024, month=3,
            base_salary='3000000', gross_pay='3300000',
            total_deduction='300000', net_pay='3000000',
        )

    def test_hr_can_view_detail(self):
        auth(self.client, get_token(self.client, 'hr3'))
        res = self.client.get(detail_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])

    def test_owner_can_view_own_detail(self):
        auth(self.client, get_token(self.client, 'emp3'))
        res = self.client.get(detail_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_other_employee_cannot_view_detail(self):
        auth(self.client, get_token(self.client, 'emp4'))
        res = self.client.get(detail_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_payroll_returns_own_records(self):
        auth(self.client, get_token(self.client, 'emp3'))
        res = self.client.get(MY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 1)

    def test_my_payroll_no_employee_returns_empty(self):
        no_link = make_user('nolink2', role='EMPLOYEE')
        auth(self.client, get_token(self.client, 'nolink2'))
        res = self.client.get(MY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data'], [])


# ── 급여 확정 테스트 ─────────────────────────────────────────────────
class PayrollConfirmTest(APITestCase):

    def setUp(self):
        dept = make_dept()
        pos  = make_pos()
        self.emp_obj  = make_employee(dept, pos)
        self.admin    = make_user('admin2', role='ADMIN')
        self.hr_user  = make_user('hr4', role='HR_MANAGER')
        self.emp_user = make_user('emp5', role='EMPLOYEE', employee=self.emp_obj)

        self.record = PayrollRecord.objects.create(
            employee=self.emp_obj, year=2024, month=4,
            base_salary='3000000', gross_pay='3300000',
            total_deduction='300000', net_pay='3000000',
            status=PayrollRecord.Status.DRAFT,
        )

    def test_admin_can_confirm(self):
        auth(self.client, get_token(self.client, 'admin2'))
        res = self.client.post(confirm_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['status'], 'CONFIRMED')
        self.assertIsNotNone(res.data['data']['confirmed_at'])

    def test_confirm_twice_fails(self):
        auth(self.client, get_token(self.client, 'admin2'))
        self.client.post(confirm_url(self.record.id))
        res = self.client.post(confirm_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_hr_cannot_confirm(self):
        auth(self.client, get_token(self.client, 'hr4'))
        res = self.client.post(confirm_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_confirm(self):
        auth(self.client, get_token(self.client, 'emp5'))
        res = self.client.post(confirm_url(self.record.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


# ── 급여대장 테스트 ──────────────────────────────────────────────────
class PayrollLedgerTest(APITestCase):

    def setUp(self):
        dept1 = make_dept('개발팀', 'DEV')
        dept2 = Department.objects.create(name='인사팀', code='HR')
        pos   = make_pos()

        self.emp1 = make_employee(dept1, pos, 'EMP001', '홍길동', '3000000')
        self.emp2 = make_employee(dept1, pos, 'EMP002', '이영희', '4000000')
        self.emp3 = make_employee(dept2, pos, 'EMP003', '박민수', '3500000')

        self.hr_user  = make_user('hr5', role='HR_MANAGER')
        self.emp_user = make_user('emp6', role='EMPLOYEE', employee=self.emp1)

        # 2024년 5월 급여대장용 데이터
        for emp, gross, ded in [
            (self.emp1, '3300000', '330000'),
            (self.emp2, '4300000', '430000'),
            (self.emp3, '3800000', '380000'),
        ]:
            PayrollRecord.objects.create(
                employee=emp, year=2024, month=5,
                base_salary=emp.base_salary,
                gross_pay=gross,
                total_deduction=ded,
                net_pay=str(Decimal(gross) - Decimal(ded)),
            )

        auth(self.client, get_token(self.client, 'hr5'))

    def test_ledger_success(self):
        res = self.client.get(LEDGER_URL, {'year': 2024, 'month': 5})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(data['year'],        2024)
        self.assertEqual(data['month'],       5)
        self.assertEqual(data['total_count'], 3)
        self.assertEqual(len(data['departments']), 2)

    def test_ledger_totals_correct(self):
        res  = self.client.get(LEDGER_URL, {'year': 2024, 'month': 5})
        data = res.data['data']
        self.assertEqual(Decimal(data['total_gross_pay']), Decimal('11400000'))
        self.assertEqual(Decimal(data['total_deduction']), Decimal('1140000'))
        self.assertEqual(Decimal(data['total_net_pay']),   Decimal('10260000'))

    def test_ledger_department_subtotals(self):
        res  = self.client.get(LEDGER_URL, {'year': 2024, 'month': 5})
        data = res.data['data']
        # 개발팀(EMP001+EMP002) 소계
        dev  = next(d for d in data['departments'] if d['name'] == '개발팀')
        self.assertEqual(dev['count'], 2)
        self.assertEqual(Decimal(dev['subtotal_gross_pay']), Decimal('7600000'))
        # 각 레코드에 employee_no, position_name 포함
        self.assertIn('employee_no',   dev['records'][0])
        self.assertIn('position_name', dev['records'][0])

    def test_ledger_empty_month(self):
        res  = self.client.get(LEDGER_URL, {'year': 2024, 'month': 6})
        data = res.data['data']
        self.assertEqual(data['total_count'], 0)
        self.assertEqual(data['departments'], [])

    def test_ledger_missing_params_fails(self):
        res = self.client.get(LEDGER_URL, {'year': 2024})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ledger_invalid_month_fails(self):
        res = self.client.get(LEDGER_URL, {'year': 2024, 'month': 13})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ledger_employee_forbidden(self):
        auth(self.client, get_token(self.client, 'emp6'))
        res = self.client.get(LEDGER_URL, {'year': 2024, 'month': 5})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ledger_unauthenticated_forbidden(self):
        self.client.credentials()
        res = self.client.get(LEDGER_URL, {'year': 2024, 'month': 5})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
