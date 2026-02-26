from django.contrib import admin

from apps.utils.encryption import decrypt, mask_resident_no
from .models import Department, Position, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('name', 'code')
    ordering      = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'level', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    ordering      = ('level',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display    = ('employee_no', 'name', 'department', 'position',
                       'hire_date', 'is_active', 'masked_rn')
    list_filter     = ('is_active', 'department', 'position')
    search_fields   = ('employee_no', 'name')
    ordering        = ('employee_no',)
    readonly_fields = ('masked_rn', 'created_at', 'updated_at')
    # 암호화 컬럼은 Admin에서 직접 수정 불가
    exclude = ('resident_no',)

    @admin.display(description='주민번호(마스킹)')
    def masked_rn(self, obj):
        return mask_resident_no(decrypt(obj.resident_no)) if obj.resident_no else '-'
