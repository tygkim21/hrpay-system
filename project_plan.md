# 인사보수시스템 프로젝트 계획서

## 개요

| 항목 | 내용 |
|------|------|
| 목적 | 직원 인사정보 및 급여/보수 통합 관리 |
| Backend | Python 3.12 · Django 4.2 · DRF 3.14 |
| Frontend | React 19 · Ant Design 6 · React Query 5 · Zustand |
| Database | MariaDB 11.3 · PyMySQL |
| 인증 | JWT (액세스 30분 / 리프레시 7일 / 블랙리스트) |
| AI | Claude Sonnet 4.6 |
| 저장소 | https://github.com/tygkim21/hrpay-system |

---

## 모듈 진행 현황

| Phase | 모듈 | 상태 | 완료일 | 테스트 수 |
|-------|------|------|--------|-----------|
| 0 | AI 작업환경 (.claude 구성) | ✅ 완료 | 2026-02-25 | - |
| 1 | 프로젝트 골격 (Django + React + MariaDB) | ✅ 완료 | 2026-02-25 | - |
| 2 | 인증/권한 (accounts 앱) | ✅ 완료 | 2026-02-25 | 9 |
| 3 | 인사관리 (employees 앱) | ✅ 완료 | 2026-02-25 | 31 |
| 4 | 근태관리 (attendance 앱) | ✅ 완료 | 2026-02-25 | 22 |
| 5 | 급여계산 (payroll 앱) | ✅ 완료 | 2026-02-26 | 19 |
| 6 | 리포트/출력 (급여대장 + PDF) | ✅ 완료 | 2026-02-26 | 8 |
| 7 | 품질검사/배포 | ⬜ 대기 | - | - |

**전체 테스트: 89개 / 전부 통과**

---

## 핵심 설계 원칙

1. **금액 필드** — `DecimalField(max_digits=15, decimal_places=2)` 필수, `FloatField` 절대 금지
2. **삭제** — `is_active=False` 소프트 삭제만 허용 (근로기준법 임금 이력 보존)
3. **API 응답** — `{"success": bool, "data": ..., "message": ""}` 형식 통일
4. **권한** — 모든 View에 `permission_classes` 명시 필수
5. **URL** — 신규 앱 URL은 `config/urls.py`에 등록

---

## 앱별 주요 모델 / 엔드포인트

### accounts
- 모델: `CustomUser` (role: ADMIN / HR_MANAGER / EMPLOYEE)
- 권한: `IsAdmin`, `IsHRManager`, `IsEmployee`, `IsOwnerOrHRManager`
- API: `/api/v1/auth/` — login, logout, refresh, me

### employees
- 모델: `Department`, `Position`, `Employee`
- 주민번호 Fernet 암호화 (`apps/utils/encryption.py`)
- API: `/api/v1/employees/`, `/api/v1/departments/`, `/api/v1/positions/`

### attendance
- 모델: `AttendanceRecord`, `AttendanceLeave`
- 출퇴근: unique_together(employee, work_date), 초과근무 480분 기준
- 휴가: PENDING → APPROVED / REJECTED 워크플로
- API: `/api/v1/attendance/`

### payroll
- 모델: `PayrollRecord` (unique_together: employee + year + month)
- 공제율: 국민연금 4.5%, 건강보험 3.545%, 장기요양 ×12.81%, 고용보험 0.9%, 소득세 2.0%, 지방소득세 ×10%
- 고정수당: 식대 200,000원, 교통비 100,000원
- 초과근무수당: 기본급 ÷ 209h × 1.5 × 초과시간
- 급여대장 API: 부서별 그룹화 + 소계 + 합계
- PDF 출력: react-to-print v3 (A4 가로)
- API: `/api/v1/payroll/`

---

## 다음 단계 (Phase 7 — 품질검사/배포)

- [ ] 프론트엔드 통합 테스트
- [ ] 보안 점검 (SECRET_KEY 강화, DEBUG=False, HTTPS)
- [ ] 운영 환경 배포 설정 (gunicorn + nginx 또는 클라우드)
- [ ] 데이터 백업 정책 수립
