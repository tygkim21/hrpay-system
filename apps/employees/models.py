from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    name       = models.CharField('부서명',   max_length=100)
    code       = models.CharField('부서코드', max_length=20, unique=True)
    is_active  = models.BooleanField('활성', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees_department'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Position(models.Model):
    name  = models.CharField('직급명', max_length=50)
    level = models.PositiveSmallIntegerField(
        '직급레벨',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='1(사원) ~ 10(대표이사)',
    )
    is_active  = models.BooleanField('활성', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees_position'
        ordering = ['level']

    def __str__(self):
        return f'{self.name} (Lv.{self.level})'


class Employee(models.Model):
    employee_no = models.CharField('사번', max_length=20, unique=True)
    name        = models.CharField('이름', max_length=50)
    # Fernet 암호화된 주민등록번호. 평문 접근은 apps.utils.encryption 사용
    resident_no = models.CharField('주민등록번호', max_length=255, blank=True)
    department  = models.ForeignKey(
        Department, on_delete=models.PROTECT,
        verbose_name='부서', related_name='employees',
    )
    position = models.ForeignKey(
        Position, on_delete=models.PROTECT,
        verbose_name='직급', related_name='employees',
    )
    hire_date   = models.DateField('입사일')
    resign_date = models.DateField('퇴사일', null=True, blank=True)
    base_salary = models.DecimalField('기본급', max_digits=15, decimal_places=2)
    is_active   = models.BooleanField('재직여부', default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees_employee'
        ordering = ['employee_no']

    def __str__(self):
        return f'[{self.employee_no}] {self.name}'
