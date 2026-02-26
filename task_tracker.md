# 작업 진척 트래커

## 전체 진척률: ✅✅✅✅✅✅✅⬜ 87% (Phase 0~6 완료 / Phase 7 대기)

**테스트 현황**: 89개 전체 통과 (accounts 9 / employees 31 / attendance 22 / payroll 27)
**최종 업데이트**: 2026-02-26

---

## Phase 0. AI 작업환경
- [x] `.claude/` 폴더 구조 생성
- [x] `settings.json` 작성 (권한·훅·환경변수)
- [x] `skills/` 3개 파일 작성 (backend, frontend, db)
- [x] `agents/` 4개 파일 작성 (planning, quality, review, test)
- [x] `hooks/` 파일 작성 (pre_hook.py, post_hook.py)
- [x] `context_log.md` / `MEMORY.md` 초기 작성

## Phase 1. 프로젝트 골격
- [x] Python 가상환경 + Django 설치
- [x] MariaDB 연결 설정 (PyMySQL, .env)
- [x] Django 앱 4개 스캐폴딩 (accounts, employees, attendance, payroll)
- [x] React 프로젝트 생성 (CRA)
- [x] Axios 인스턴스 + JWT 인터셉터 구성
- [x] CORS 설정

## Phase 2. 인증/권한
- [x] `CustomUser` 모델 (role 필드)
- [x] JWT 로그인·로그아웃·리프레시 API
- [x] 권한 클래스 4종 (IsAdmin, IsHRManager, IsEmployee, IsOwnerOrHRManager)
- [x] `/api/v1/auth/me/` 엔드포인트
- [x] 토큰 블랙리스트 활성화
- [x] React 로그인 화면 + Zustand 인증 상태
- [x] Axios 401 자동 갱신 인터셉터
- [x] 테스트 9개

## Phase 3. 인사관리
- [x] `Department`, `Position`, `Employee` 모델
- [x] 주민번호 Fernet 암호화 (`apps/utils/encryption.py`)
- [x] 직원 CRUD API (목록·상세·등록·수정·퇴직)
- [x] 부서·직급 CRUD API
- [x] 목록 마스킹 / 상세 복호화 후 마스킹
- [x] 퇴직 소프트 삭제 (IsAdmin 전용)
- [x] React 직원 목록·상세·등록·수정 페이지
- [x] 테스트 31개

## Phase 4. 근태관리
- [x] `CustomUser.employee` OneToOneField 추가 (0002 마이그레이션)
- [x] `AttendanceRecord` 모델 (unique: employee+work_date)
- [x] `AttendanceLeave` 모델 (PENDING→APPROVED/REJECTED)
- [x] 출퇴근 API (check-in, check-out, 초과근무 480분 기준)
- [x] 월별 근태 조회 API
- [x] 휴가 신청·승인·반려 API
- [x] `_extract_error()` 헬퍼 (ErrorDetail 노출 버그 방지)
- [x] React 출퇴근 페이지, 휴가 목록·신청 페이지
- [x] 테스트 22개

## Phase 5. 급여관리
- [x] `PayrollRecord` 모델 (unique: employee+year+month, 17개 금액 필드 전부 DecimalField)
- [x] `PayrollService.calculate()` — 4대보험·소득세 공제, 원 단위 절사
- [x] `PayrollService.confirm()` — DRAFT → CONFIRMED
- [x] 급여 계산 API (`POST /calculate/`, IsHRManager)
- [x] 급여 목록 API (`GET /`, year/month 필터, IsHRManager)
- [x] 급여 상세 API (`GET /<id>/`, 본인 or HR)
- [x] 급여 확정 API (`POST /<id>/confirm/`, IsAdmin)
- [x] 내 급여 API (`GET /my/`, IsEmployee)
- [x] `PayrollRecordSerializer` (전 필드 read-only)
- [x] React 급여 목록·상세·내 급여 페이지
- [x] 테스트 19개

## Phase 6. 리포트/출력
- [x] `LedgerRecordSerializer` (사번·직급 포함)
- [x] 급여대장 API (`GET /reports/ledger/`, 부서별 그룹화·소계·합계)
- [x] `react-to-print` v3 설치
- [x] React 급여대장 페이지 (`/payroll/ledger`)
- [x] A4 가로 PDF 출력 (pageStyle CSS)
- [x] 테스트 8개

## Phase 7. 품질검사/배포 ⬜ 대기
- [ ] 프론트엔드 통합 테스트
- [ ] 보안 점검 (SECRET_KEY, DEBUG=False, HTTPS, ALLOWED_HOSTS)
- [ ] 운영 환경 설정 (gunicorn + nginx 또는 클라우드)
- [ ] 정적 파일 서빙 (`collectstatic`)
- [ ] 데이터 백업 정책
- [ ] 운영 배포

---

## 부록 — 주요 파일 위치

| 분류 | 경로 |
|------|------|
| Django 설정 | `config/settings.py` |
| URL 라우팅 | `config/urls.py` |
| PyMySQL 설정 | `config/__init__.py` |
| 인증 앱 | `apps/accounts/` |
| 암호화 유틸 | `apps/utils/encryption.py` |
| Axios 인스턴스 | `frontend/src/api/axiosInstance.js` |
| 인증 상태 | `frontend/src/store/authStore.js` |
| 환경변수 샘플 | `.env.example` |
