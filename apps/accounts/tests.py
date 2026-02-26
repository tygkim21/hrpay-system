from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()
LOGIN_URL  = '/api/v1/auth/login/'
LOGOUT_URL = '/api/v1/auth/logout/'
ME_URL     = '/api/v1/auth/me/'
REFRESH_URL = '/api/v1/auth/refresh/'


def create_user(username='testuser', password='testpass123', role='EMPLOYEE'):
    return User.objects.create_user(username=username, password=password, role=role)


class LoginTest(APITestCase):

    def setUp(self):
        self.user = create_user()

    def test_login_success(self):
        res = self.client.post(LOGIN_URL, {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertIn('access', res.data['data'])
        self.assertIn('refresh', res.data['data'])

    def test_login_wrong_password(self):
        res = self.client.post(LOGIN_URL, {'username': 'testuser', 'password': 'wrong'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post(LOGIN_URL, {'username': 'testuser', 'password': 'testpass123'})
        self.assertFalse(res.data['success'])

    def test_login_missing_fields(self):
        res = self.client.post(LOGIN_URL, {'username': 'testuser'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        res = self.client.post(LOGIN_URL, {'username': 'testuser', 'password': 'testpass123'})
        self.access  = res.data['data']['access']
        self.refresh = res.data['data']['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_logout_success(self):
        res = self.client.post(LOGOUT_URL, {'refresh': self.refresh})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])

    def test_logout_without_token(self):
        self.client.credentials()
        res = self.client.post(LOGOUT_URL, {'refresh': self.refresh})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalid_refresh_token(self):
        res = self.client.post(LOGOUT_URL, {'refresh': 'invalid.token.value'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])


class MeTest(APITestCase):

    def setUp(self):
        self.user = create_user(role='HR_MANAGER')
        res = self.client.post(LOGIN_URL, {'username': 'testuser', 'password': 'testpass123'})
        self.access = res.data['data']['access']

    def test_me_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['username'], 'testuser')
        self.assertEqual(res.data['data']['role'], 'HR_MANAGER')

    def test_me_without_auth(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
