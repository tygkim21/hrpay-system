# 맥락 노트 (결정 이유 기록)

## 기술 선택 결정

- **JWT 인증**: React SPA 환경에서 세션 복잡도 회피
- **Zustand**: Redux 대비 가볍고 React Query와 역할 분리 명확 (서버 상태 ↔ 클라이언트 상태)
- **DecimalField**: float 반올림 오류 방지 — 급여 계산 정확성 필수
- **소프트 삭제**: 급여 이력 보존 의무 (근로기준법)
- **PyMySQL**: Windows 환경에서 mysqlclient 빌드 이슈 회피
- **react-to-print (PDF)**: Windows + 한글 환경에서 ReportLab·WeasyPrint 의존성 문제 회피, 브라우저 네이티브 인쇄로 한글 완벽 지원

## 아키텍처 결정

- **앱 분리**: accounts / employees / attendance / payroll — 도메인 단위 분리
- **API 버전**: `/api/v1/` — 향후 v2 확장 대비
- **토큰 저장**: localStorage — httpOnly cookie 대비 단순성 선택 (내부 시스템)
- **Access Token TTL**: 30분, Refresh 7일 — 보안과 UX 균형
- **Service 레이어**: 비즈니스 로직을 View에서 분리 (PayrollService, AttendanceService 등)
- **LedgerRecordSerializer 분리**: 급여대장 전용 직렬화기 — 사번·직급 포함, 일반 PayrollRecordSerializer와 역할 분리

## Phase별 주요 결정 사항

### Phase 3 — 인사관리
- 주민번호 암호화: Fernet 대칭키, `SECRET_KEY` 기반 키 도출 → `apps/utils/encryption.py`
- 목록 조회 시 마스킹(`mask_resident_no`), 상세 조회 시 복호화 후 마스킹 → Serializer `to_representation()` 오버라이드
- EmployeeDetailSerializer: FK 입력은 ID(정수), 출력은 nested object
- URL 3분할: `urlpatterns` / `department_urlpatterns` / `position_urlpatterns` → config/urls.py에서 각각 include

### Phase 4 — 근태관리
- `CustomUser.employee` OneToOneField(null=True) 추가 → accounts/0002_add_employee_link 마이그레이션
- `_extract_error()` 헬퍼 도입: DRF ValidationError의 ErrorDetail 직접 노출 버그 방지
- 휴가 Serializer: `employee` 필드 `read_only_fields` 포함 필수 — view에서 `user.employee`로 자동 주입
- 초과근무 계산: `max(0, total_minutes - 480)`

### Phase 5 — 급여관리
- 공제 금액: `Decimal.quantize(Decimal('1'), rounding=ROUND_FLOOR)` 원 단위 절사
- 초과근무수당: `기본급 / 209 × 1.5 × 초과시간(h)` — 209시간은 법정 월 소정근로시간
- PayrollDetailView: `IsOwnerOrHRManager` 대신 view 내부에서 직접 `role`·`employee_id` 비교 → 객체 레벨 권한과 view 레벨 권한 충돌 방지
- status: DRAFT(초안) → CONFIRMED(확정), 확정은 Admin 전용

### Phase 6 — 리포트/출력
- 급여대장 API(`/api/v1/payroll/reports/ledger/`): `itertools.groupby`로 부서 그룹화, 소계/합계 계산
- PDF: react-to-print v3 `contentRef` API 사용, `pageStyle`에 `@page { size: A4 landscape }` 지정
- 라우트 순서: `/payroll/ledger`를 `/payroll/:id` 앞에 등록 — React Router 경로 충돌 방지

## 알려진 주의사항

- `.env` 파일 — git 추적 금지 (`.gitignore` 등록 완료), DB 비밀번호 포함
- `__pycache__` / `*.pyc` — `.gitignore` 등록 완료
- 테스트 DB: `hrpay_user`에 `GRANT ALL PRIVILEGES ON test_hrpay_db.*` 별도 부여 필요

## Phase 진행 현황

| Phase | 내용 | 상태 | 완료일 |
|-------|------|------|--------|
| 0 | AI 작업환경 (.claude 구성) | ✅ 완료 | 2026-02-25 |
| 1 | 프로젝트 골격 | ✅ 완료 | 2026-02-25 |
| 2 | 인증/권한 (accounts 앱) | ✅ 완료 | 2026-02-25 |
| 3 | 인사관리 (employees 앱) | ✅ 완료 | 2026-02-25 |
| 4 | 근태관리 (attendance 앱) | ✅ 완료 | 2026-02-25 |
| 5 | 급여계산 (payroll 앱) | ✅ 완료 | 2026-02-26 |
| 6 | 리포트/출력 (급여대장 + PDF) | ✅ 완료 | 2026-02-26 |
| 7 | 품질검사/배포 | ⬜ 대기 | - |
