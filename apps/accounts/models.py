from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('사용자 ID는 필수입니다.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN      = 'ADMIN',      '시스템 관리자'
        HR_MANAGER = 'HR_MANAGER', '인사/급여 담당자'
        EMPLOYEE   = 'EMPLOYEE',   '일반 직원'

    username   = models.CharField('사용자 ID', max_length=50, unique=True)
    role       = models.CharField('권한', max_length=20,
                                  choices=Role.choices, default=Role.EMPLOYEE)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 직원 테이블과 연결
    employee = models.OneToOneField(
        'employees.Employee',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='user',
        verbose_name='연결된 직원',
    )

    objects = CustomUserManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'accounts_user'
        verbose_name = '사용자'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
