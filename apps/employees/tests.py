import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.utils.encryption import encrypt, decrypt
from .models import Department, Position, Employee

User = get_user_model()

DEPT_URL = '/api/v1/departments/'
POS_URL  = '/api/v1/positions/'
EMP_URL  = '/api/v1/employees/'


# ── 공통 헬퍼 ────────────────────────────────────────────────────
def make_user(username, password='pass1234', role='EMPLOYEE'):
    return User.objects.create_user(username=username, password=password, role=role)

def get_token(client, username, password='pass1234'):
    res = client.post('/api/v1/auth/login/', {'username': username, 'password': password})
    return res.data['data']['access']

def auth(client, token):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

def make_dept(name='개발팀', code='DEV'):
    return Department.objects.create(name=name, code=code)

def make_pos(name='사원', level=1):
    return Position.objects.create(name=name, level=level)

def make_employee(dept, pos, employee_no='EMP001', name='홍길동',
                  resident_no='990101-1234567', base_salary='3000000'):
    return Employee.objects.create(
        employee_no=employee_no,
        name=name,
        resident_no=encrypt(resident_no),
        department=dept,
        position=pos,
        hire_date=datetime.date(2024, 1, 1),
        base_salary=base_salary,
    )


# ── 부서 API 테스트 ──────────────────────────────────────────────
class DepartmentAPITest(APITestCase):

    def setUp(self):
        self.hr  = make_user('hr',  role='HR_MANAGER')
        self.emp = make_user('emp', role='EMPLOYEE')
        auth(self.client, get_token(self.client, 'hr'))

    def test_create_department_success(self):
        res = self.client.post(DEPT_URL, {'name': '개발팀', 'code': 'DEV'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['code'], 'DEV')

    def test_list_departments(self):
        make_dept('개발팀', 'DEV')
        make_dept('인사팀', 'HR')
        res = self.client.get(DEPT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 2)

    def test_employee_cannot_create_department(self):
        auth(self.client, get_token(self.client, 'emp'))
        res = self.client.post(DEPT_URL, {'name': '개발팀', 'code': 'DEV'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_code_fails(self):
        make_dept('개발팀', 'DEV')
        res = self.client.post(DEPT_URL, {'name': '개발2팀', 'code': 'DEV'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_unauthenticated_fails(self):
        self.client.credentials()
        res = self.client.get(DEPT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 직급 API 테스트 ──────────────────────────────────────────────
class PositionAPITest(APITestCase):

    def setUp(self):
        self.hr = make_user('hr', role='HR_MANAGER')
        auth(self.client, get_token(self.client, 'hr'))

    def test_create_position_success(self):
        res = self.client.post(POS_URL, {'name': '사원', 'level': 1})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])

    def test_level_out_of_range_fails(self):
        res = self.client.post(POS_URL, {'name': '초월직급', 'level': 11})
        self.assertFalse(res.data['success'])

    def test_list_positions(self):
        make_pos('사원', 1)
        make_pos('대리', 2)
        res = self.client.get(POS_URL)
        self.assertEqual(len(res.data['data']), 2)


# ── 직원 API 테스트 ──────────────────────────────────────────────
class EmployeeAPITest(APITestCase):

    def setUp(self):
        self.dept  = make_dept()
        self.pos   = make_pos()
        self.hr    = make_user('hr',    role='HR_MANAGER')
        self.admin = make_user('admin', role='ADMIN')
        auth(self.client, get_token(self.client, 'hr'))

        self.emp_data = {
            'employee_no': 'EMP001',
            'name':        '홍길동',
            'resident_no': '990101-1234567',
            'department':  self.dept.id,
            'position':    self.pos.id,
            'hire_date':   '2024-01-01',
            'base_salary': '3000000.00',
        }

    # ── 등록 ────────────────────────────────────────────────────
    def test_create_employee_success(self):
        res = self.client.post(EMP_URL, self.emp_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        # 주민번호 마스킹 확인
        self.assertIn('*', res.data['data']['resident_no'])
        self.assertNotIn('1234567', res.data['data']['resident_no'])

    def test_resident_no_encrypted_in_db(self):
        self.client.post(EMP_URL, self.emp_data)
        emp = Employee.objects.get(employee_no='EMP001')
        self.assertNotEqual(emp.resident_no, '990101-1234567')
        self.assertEqual(decrypt(emp.resident_no), '990101-1234567')

    def test_duplicate_employee_no_fails(self):
        make_employee(self.dept, self.pos)
        res = self.client.post(EMP_URL, self.emp_data)
        self.assertFalse(res.data['success'])

    def test_invalid_resident_no_fails(self):
        data = {**self.emp_data, 'resident_no': '12345'}
        res  = self.client.post(EMP_URL, data)
        self.assertFalse(res.data['success'])

    def test_negative_salary_fails(self):
        data = {**self.emp_data, 'base_salary': '-1000'}
        res  = self.client.post(EMP_URL, data)
        self.assertFalse(res.data['success'])

    def test_employee_role_cannot_register(self):
        make_user('emp2', role='EMPLOYEE')
        auth(self.client, get_token(self.client, 'emp2'))
        res = self.client.post(EMP_URL, self.emp_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── 목록 조회 ────────────────────────────────────────────────
    def test_list_employees(self):
        make_employee(self.dept, self.pos, 'EMP001', '홍길동')
        make_employee(self.dept, self.pos, 'EMP002', '김철수')
        res = self.client.get(EMP_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 2)

    def test_list_excludes_salary_and_resident_no(self):
        make_employee(self.dept, self.pos)
        res = self.client.get(EMP_URL)
        row = res.data['data'][0]
        self.assertNotIn('base_salary',  row)
        self.assertNotIn('resident_no',  row)

    def test_search_by_name(self):
        make_employee(self.dept, self.pos, 'EMP001', '홍길동')
        make_employee(self.dept, self.pos, 'EMP002', '김철수')
        res = self.client.get(EMP_URL, {'search': '홍'})
        self.assertEqual(len(res.data['data']), 1)
        self.assertEqual(res.data['data'][0]['name'], '홍길동')

    def test_search_by_employee_no(self):
        make_employee(self.dept, self.pos, 'EMP001', '홍길동')
        make_employee(self.dept, self.pos, 'EMP002', '김철수')
        res = self.client.get(EMP_URL, {'search': 'EMP002'})
        self.assertEqual(len(res.data['data']), 1)

    def test_filter_by_department(self):
        dept2 = make_dept('인사팀', 'HR')
        make_employee(self.dept,  self.pos, 'EMP001', '홍길동')
        make_employee(dept2,      self.pos, 'EMP002', '김철수')
        res = self.client.get(EMP_URL, {'department': self.dept.id})
        self.assertEqual(len(res.data['data']), 1)

    def test_filter_active_only(self):
        make_employee(self.dept, self.pos, 'EMP001', '재직자')
        emp2 = make_employee(self.dept, self.pos, 'EMP002', '퇴직자')
        emp2.is_active = False
        emp2.save()
        res = self.client.get(EMP_URL, {'is_active': 'true'})
        self.assertEqual(len(res.data['data']), 1)
        self.assertEqual(res.data['data'][0]['name'], '재직자')

    # ── 상세 조회 ────────────────────────────────────────────────
    def test_get_employee_detail_includes_salary(self):
        emp = make_employee(self.dept, self.pos)
        res = self.client.get(f'{EMP_URL}{emp.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('base_salary', res.data['data'])
        self.assertIn('resident_no', res.data['data'])
        self.assertIn('*', res.data['data']['resident_no'])

    def test_get_nonexistent_employee_returns_404(self):
        res = self.client.get(f'{EMP_URL}99999/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # ── 수정 ────────────────────────────────────────────────────
    def test_update_employee_name(self):
        emp = make_employee(self.dept, self.pos)
        res = self.client.put(f'{EMP_URL}{emp.id}/', {'name': '이순신'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['name'], '이순신')

    def test_update_does_not_change_resident_no_if_omitted(self):
        emp = make_employee(self.dept, self.pos)
        original_enc = emp.resident_no
        self.client.put(f'{EMP_URL}{emp.id}/', {'name': '이순신'}, format='json')
        emp.refresh_from_db()
        self.assertEqual(emp.resident_no, original_enc)

    def test_update_resident_no_re_encrypts(self):
        emp = make_employee(self.dept, self.pos)
        self.client.put(
            f'{EMP_URL}{emp.id}/',
            {'resident_no': '880202-2345678'},
            format='json',
        )
        emp.refresh_from_db()
        self.assertEqual(decrypt(emp.resident_no), '880202-2345678')

    # ── 퇴직 처리 ────────────────────────────────────────────────
    def test_resign_as_admin_success(self):
        emp = make_employee(self.dept, self.pos)
        auth(self.client, get_token(self.client, 'admin'))
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {'resign_date': '2024-12-31'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['data']['is_active'])
        self.assertEqual(res.data['data']['resign_date'], '2024-12-31')

    def test_resign_as_hr_manager_forbidden(self):
        emp = make_employee(self.dept, self.pos)
        # 현재 인증: HR_MANAGER
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {'resign_date': '2024-12-31'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_resign_before_hire_date_fails(self):
        emp = make_employee(self.dept, self.pos)   # hire_date = 2024-01-01
        auth(self.client, get_token(self.client, 'admin'))
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {'resign_date': '2023-12-31'})
        self.assertFalse(res.data['success'])

    def test_resign_already_resigned_fails(self):
        emp = make_employee(self.dept, self.pos)
        emp.is_active = False
        emp.save()
        auth(self.client, get_token(self.client, 'admin'))
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {'resign_date': '2024-12-31'})
        self.assertFalse(res.data['success'])

    def test_resign_missing_date_fails(self):
        emp = make_employee(self.dept, self.pos)
        auth(self.client, get_token(self.client, 'admin'))
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {})
        self.assertFalse(res.data['success'])

    def test_resign_invalid_date_format_fails(self):
        emp = make_employee(self.dept, self.pos)
        auth(self.client, get_token(self.client, 'admin'))
        res = self.client.post(f'{EMP_URL}{emp.id}/resign/', {'resign_date': '2024/12/31'})
        self.assertFalse(res.data['success'])
