import axiosInstance from './axiosInstance';

// ── 직원 ─────────────────────────────────────────────────────────
export const getEmployees = (params) =>
  axiosInstance.get('/employees/', { params });

export const getEmployee = (id) =>
  axiosInstance.get(`/employees/${id}/`);

export const createEmployee = (data) =>
  axiosInstance.post('/employees/', data);

export const updateEmployee = (id, data) =>
  axiosInstance.put(`/employees/${id}/`, data);

export const resignEmployee = (id, data) =>
  axiosInstance.post(`/employees/${id}/resign/`, data);

// ── 부서 ─────────────────────────────────────────────────────────
export const getDepartments = () =>
  axiosInstance.get('/departments/');

export const createDepartment = (data) =>
  axiosInstance.post('/departments/', data);

// ── 직급 ─────────────────────────────────────────────────────────
export const getPositions = () =>
  axiosInstance.get('/positions/');

export const createPosition = (data) =>
  axiosInstance.post('/positions/', data);
