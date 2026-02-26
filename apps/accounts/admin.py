from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username',)
    ordering = ('-created_at',)
    fieldsets = (
        (None,          {'fields': ('username', 'password')}),
        ('권한 설정',    {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('그룹/퍼미션', {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
