from django.conf import settings
from django.db import models


class AttendanceRecord(models.Model):
    """출퇴근 기록"""

    employee         = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='attendance_records',
        verbose_name='직원',
    )
    work_date        = models.DateField('근무일')
    check_in         = models.DateTimeField('출근시각', null=True, blank=True)
    check_out        = models.DateTimeField('퇴근시각', null=True, blank=True)
    work_minutes     = models.PositiveIntegerField('실근무분', default=0)
    overtime_minutes = models.PositiveIntegerField('초과근무분', default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_record'
        unique_together = ('employee', 'work_date')
        verbose_name = '출퇴근 기록'
        verbose_name_plural = '출퇴근 기록 목록'
        ordering = ['-work_date']

    def __str__(self):
        return f'{self.employee.name} {self.work_date}'


class AttendanceLeave(models.Model):
    """휴가 신청"""

    class LeaveType(models.TextChoices):
        ANNUAL  = 'ANNUAL',  '연차'
        HALF    = 'HALF',    '반차'
        SICK    = 'SICK',    '병가'
        SPECIAL = 'SPECIAL', '특별휴가'

    class Status(models.TextChoices):
        PENDING  = 'PENDING',  '신청'
        APPROVED = 'APPROVED', '승인'
        REJECTED = 'REJECTED', '반려'

    employee      = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='leaves',
        verbose_name='직원',
    )
    leave_type    = models.CharField('휴가종류', max_length=10, choices=LeaveType.choices)
    start_date    = models.DateField('시작일')
    end_date      = models.DateField('종료일')
    reason        = models.TextField('사유', blank=True)
    status        = models.CharField(
        '상태', max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approver      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_leaves',
        verbose_name='승인자',
    )
    approved_at   = models.DateTimeField('승인일시', null=True, blank=True)
    reject_reason = models.TextField('반려사유', blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_leave'
        verbose_name = '휴가 신청'
        verbose_name_plural = '휴가 신청 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee.name} {self.get_leave_type_display()} {self.start_date}~{self.end_date}'
