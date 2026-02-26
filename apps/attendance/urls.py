from django.urls import path

from .views import (
    CheckInView,
    CheckOutView,
    MonthlyAttendanceView,
    LeaveListCreateView,
    LeaveApprovalView,
)

urlpatterns = [
    path('check-in/',      CheckInView.as_view(),          name='attendance-check-in'),
    path('check-out/',     CheckOutView.as_view(),          name='attendance-check-out'),
    path('monthly/',       MonthlyAttendanceView.as_view(), name='attendance-monthly'),
    path('leaves/',        LeaveListCreateView.as_view(),   name='leave-list-create'),
    path('leaves/<int:pk>/approve/', LeaveApprovalView.as_view(), name='leave-approval'),
]
