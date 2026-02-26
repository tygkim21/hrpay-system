import axiosInstance from './axiosInstance';

// ── 출퇴근 ────────────────────────────────────────────────────────
export const checkIn  = ()           => axiosInstance.post('/attendance/check-in/');
export const checkOut = ()           => axiosInstance.post('/attendance/check-out/');
export const getMonthlyAttendance = (year, month) =>
  axiosInstance.get('/attendance/monthly/', { params: { year, month } });

// ── 휴가 ──────────────────────────────────────────────────────────
export const getLeaves      = ()     => axiosInstance.get('/attendance/leaves/');
export const requestLeave   = (data) => axiosInstance.post('/attendance/leaves/', data);
export const approveLeave   = (id, data) =>
  axiosInstance.post(`/attendance/leaves/${id}/approve/`, data);
