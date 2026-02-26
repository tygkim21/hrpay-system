import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
});

// ── 요청 인터셉터: 모든 요청에 JWT 자동 첨부 ──────────
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ── 응답 인터셉터: 토큰 만료 시 자동 갱신 ─────────────
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // 401 오류 + 재시도 아닌 경우 → 토큰 갱신 시도
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refresh = localStorage.getItem('refresh_token');
                const res = await axios.post(
                    'http://localhost:8000/api/v1/auth/refresh/',
                    { refresh }
                );
                const newAccess = res.data.data.access;
                localStorage.setItem('access_token', newAccess);
                originalRequest.headers.Authorization = `Bearer ${newAccess}`;
                return axiosInstance(originalRequest);   // 원래 요청 재시도

            } catch (refreshError) {
                // Refresh도 만료 → 로그인 페이지로
                localStorage.clear();
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
