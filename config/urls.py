from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from apps.employees.urls import department_urlpatterns, position_urlpatterns


def health_check(request):
    """서버 상태 확인용 엔드포인트"""
    return JsonResponse({"success": True, "data": None, "message": "서버 정상 동작 중"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check),

    # Phase 2 — 인증/권한
    path('api/v1/auth/', include('apps.accounts.urls')),

    # Phase 3 — 인사관리
    path('api/v1/employees/',  include('apps.employees.urls')),
    path('api/v1/departments/', include((department_urlpatterns, 'departments'))),
    path('api/v1/positions/',   include((position_urlpatterns,   'positions'))),

    # Phase 4 — 근태관리
    path('api/v1/attendance/', include('apps.attendance.urls')),

    # Phase 5 — 급여관리
    path('api/v1/payroll/', include('apps.payroll.urls')),
]
