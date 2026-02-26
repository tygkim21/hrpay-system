import axiosInstance from './axiosInstance';

export const getPayrolls    = (params) => axiosInstance.get('/payroll/', { params });
export const calculatePayroll = (data) => axiosInstance.post('/payroll/calculate/', data);
export const getPayroll     = (id)    => axiosInstance.get(`/payroll/${id}/`);
export const confirmPayroll = (id)    => axiosInstance.post(`/payroll/${id}/confirm/`);
export const getMyPayrolls   = ()       => axiosInstance.get('/payroll/my/');
export const getPayrollLedger = (params) => axiosInstance.get('/payroll/reports/ledger/', { params });
