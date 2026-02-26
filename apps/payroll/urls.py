from django.urls import path

from .views import (
    CalculatePayrollView,
    PayrollListView,
    PayrollDetailView,
    ConfirmPayrollView,
    MyPayrollView,
    PayrollLedgerView,
)

urlpatterns = [
    path('calculate/',              CalculatePayrollView.as_view()),
    path('my/',                     MyPayrollView.as_view()),
    path('reports/ledger/',         PayrollLedgerView.as_view()),
    path('',                        PayrollListView.as_view()),
    path('<int:pk>/',               PayrollDetailView.as_view()),
    path('<int:pk>/confirm/',       ConfirmPayrollView.as_view()),
]
