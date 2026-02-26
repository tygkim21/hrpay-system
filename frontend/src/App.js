import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import EmployeeListPage   from './pages/EmployeeListPage';
import EmployeeDetailPage from './pages/EmployeeDetailPage';
import EmployeeFormPage   from './pages/EmployeeFormPage';
import AttendancePage     from './pages/AttendancePage';
import MyAttendancePage   from './pages/MyAttendancePage';
import LeaveRequestPage   from './pages/LeaveRequestPage';
import PayrollListPage    from './pages/PayrollListPage';
import PayrollDetailPage  from './pages/PayrollDetailPage';
import MyPayrollPage      from './pages/MyPayrollPage';
import PayrollLedgerPage  from './pages/PayrollLedgerPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry:              1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* 직원 관리 */}
          <Route path="/employees"          element={<EmployeeListPage />} />
          <Route path="/employees/new"      element={<EmployeeFormPage />} />
          <Route path="/employees/:id"      element={<EmployeeDetailPage />} />
          <Route path="/employees/:id/edit" element={<EmployeeFormPage />} />

          {/* 근태 관리 */}
          <Route path="/attendance"   element={<AttendancePage />} />
          <Route path="/leaves"       element={<MyAttendancePage />} />
          <Route path="/leaves/new"   element={<LeaveRequestPage />} />

          {/* 급여 관리 */}
          <Route path="/payroll"        element={<PayrollListPage />} />
          <Route path="/payroll/ledger" element={<PayrollLedgerPage />} />
          <Route path="/payroll/:id"    element={<PayrollDetailPage />} />
          <Route path="/my-payroll"     element={<MyPayrollPage />} />

          {/* 루트 → 직원 목록으로 리다이렉트 */}
          <Route path="/" element={<Navigate to="/employees" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
