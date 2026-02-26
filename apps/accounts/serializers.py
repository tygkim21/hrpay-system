# apps/accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
        if not user.is_active:
            raise serializers.ValidationError('비활성화된 계정입니다.')
        data['user'] = user
        return data


class UserInfoSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model  = CustomUser
        fields = ['id', 'username', 'role', 'role_display', 'employee_id']
