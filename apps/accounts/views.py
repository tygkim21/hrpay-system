# apps/accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer, UserInfoSerializer


def success_response(data=None, message='', status_code=200):
    """통일된 성공 응답"""
    return Response(
        {"success": True, "data": data, "message": message},
        status=status_code
    )

def error_response(message='', status_code=400):
    """통일된 실패 응답"""
    return Response(
        {"success": False, "data": None, "message": message},
        status=status_code
    )


class LoginView(APIView):
    permission_classes = [AllowAny]   # 로그인은 인증 불필요

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))

        user    = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return success_response(data={
            "access" : str(refresh.access_token),
            "refresh": str(refresh),
            "user"   : UserInfoSerializer(user).data,
        }, message='로그인 성공')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()   # 토큰 블랙리스트 처리
            return success_response(message='로그아웃 성공')
        except Exception:
            return error_response('유효하지 않은 토큰입니다.')


class MeView(APIView):
    """현재 로그인 사용자 정보 조회"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserInfoSerializer(request.user).data)
