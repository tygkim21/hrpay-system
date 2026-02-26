from django.urls import path
from . import views

# /api/v1/employees/ 하위 URL
urlpatterns = [
    path('',              views.EmployeeListView.as_view(),   name='employee-list'),
    path('<int:pk>/',     views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('<int:pk>/resign/', views.EmployeeResignView.as_view(), name='employee-resign'),
]

# /api/v1/departments/ 에서 include로 사용
department_urlpatterns = [
    path('', views.DepartmentListView.as_view(), name='department-list'),
]

# /api/v1/positions/ 에서 include로 사용
position_urlpatterns = [
    path('', views.PositionListView.as_view(), name='position-list'),
]
