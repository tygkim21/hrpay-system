# 인사보수시스템 (HR & Payroll System)

직원 정보 관리부터 근태, 급여 계산·확정, 급여대장 PDF 출력까지 통합 관리하는 웹 기반 인사보수 시스템입니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python 3.12 · Django 4.2 · Django REST Framework 3.14 |
| 인증 | JWT (djangorestframework-simplejwt 5.5) |
| Database | MariaDB 11.3 · PyMySQL |
| Frontend | React 19 · Ant Design 6 · React Query 5 · Zustand · React Router 7 |
| PDF 출력 | react-to-print 3 (브라우저 인쇄 → PDF) |

---

## 주요 기능

### 인증 (Phase 2)
- 사용자 역할 3종: `ADMIN` / `HR_MANAGER` / `EMPLOYEE`
- JWT 액세스 토큰(30분) + 리프레시 토큰(7일) + 블랙리스트

### 인사관리 (Phase 3)
- 부서·직급·직원 CRUD
- 주민등록번호 Fernet 암호화 저장, 목록 조회 시 마스킹
- 퇴직 처리 소프트 삭제 (`is_active=False`)

### 근태관리 (Phase 4)
- 출·퇴근 기록, 실근무시간·초과근무시간 자동 계산 (기준 480분)
- 연차·병가·기타 휴가 신청 → HR 승인/반려 워크플로

### 급여관리 (Phase 5)
- 기본급 스냅샷 + 고정수당(식대 20만·교통비 10만) + 초과근무수당 자동 계산
- 2024년 기준 4대보험·소득세 공제 (원 단위 절사)
- DRAFT → CONFIRMED 확정 워크플로 (Admin 전용)

### 리포트/출력 (Phase 6)
- 부서별 급여대장 조회 (소계·합계 포함)
- A4 가로 PDF 출력 (react-to-print, 한글 완벽 지원)

---

## 공제율 (2024년 기준)

| 항목 | 요율 |
|------|------|
| 국민연금 | 4.5% |
| 건강보험 | 3.545% |
| 장기요양보험 | 건강보험료 × 12.81% |
| 고용보험 | 0.9% |
| 소득세 | 2.0% (간이세액 근사값) |
| 지방소득세 | 소득세 × 10% |

---

## 프로젝트 구조

```
hrpay-system/
├── config/                  # Django 설정 (settings, urls, wsgi, asgi)
├── apps/
│   ├── accounts/            # 인증·권한 (CustomUser, JWT, 권한 4종)
│   ├── employees/           # 인사관리 (Department, Position, Employee)
│   ├── attendance/          # 근태관리 (AttendanceRecord, AttendanceLeave)
│   ├── payroll/             # 급여관리 (PayrollRecord, 급여대장 API)
│   └── utils/               # 공통 유틸 (Fernet 암호화)
├── frontend/
│   └── src/
│       ├── api/             # Axios 인스턴스, 앱별 API 함수
│       ├── components/      # 공통 컴포넌트
│       ├── pages/           # 페이지 컴포넌트
│       └── store/           # Zustand 상태
├── manage.py
└── requirements.txt
```

---

## API 엔드포인트

```
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/refresh/
GET    /api/v1/auth/me/

GET    /api/v1/departments/
GET    /api/v1/positions/
GET    /api/v1/employees/
GET    /api/v1/employees/<id>/
POST   /api/v1/employees/<id>/resign/

POST   /api/v1/attendance/check-in/
POST   /api/v1/attendance/check-out/
GET    /api/v1/attendance/monthly/
GET    /api/v1/attendance/leaves/
POST   /api/v1/attendance/leaves/
POST   /api/v1/attendance/leaves/<id>/approve/

POST   /api/v1/payroll/calculate/
GET    /api/v1/payroll/
GET    /api/v1/payroll/<id>/
POST   /api/v1/payroll/<id>/confirm/
GET    /api/v1/payroll/my/
GET    /api/v1/payroll/reports/ledger/
```

---

## 로컬 실행

### 사전 요구사항
- Python 3.12+
- Node.js 18+
- MariaDB 11.3+

### Backend

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정 (.env 파일 생성)
cp .env.example .env          # 아래 환경변수 섹션 참고

# 4. 마이그레이션
python manage.py migrate

# 5. 관리자 계정 생성
python manage.py createsuperuser

# 6. 개발 서버 실행
python manage.py runserver 8000
```

### Frontend

```bash
cd frontend
npm install
npm start          # http://localhost:3000
```

### 테스트

```bash
# 전체 테스트 (89개)
python manage.py test apps --verbosity=2

# 앱별 실행
python manage.py test apps.accounts
python manage.py test apps.employees
python manage.py test apps.attendance
python manage.py test apps.payroll
```

---

## 환경변수 (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=hrpay_db
DB_USER=hrpay_user
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### MariaDB 초기 설정

```sql
CREATE DATABASE hrpay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hrpay_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON hrpay_db.* TO 'hrpay_user'@'localhost';

-- 테스트 DB 권한 (테스트 실행 시 필요)
GRANT ALL PRIVILEGES ON test_hrpay_db.* TO 'hrpay_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 프론트엔드 라우트

| URL | 페이지 | 권한 |
|-----|--------|------|
| `/employees` | 직원 목록 | HR_MANAGER+ |
| `/employees/:id` | 직원 상세 | HR_MANAGER+ |
| `/attendance` | 출퇴근 관리 | 전체 |
| `/leaves` | 휴가 관리 | 전체 |
| `/payroll` | 급여 목록 | HR_MANAGER+ |
| `/payroll/ledger` | 급여대장 (PDF) | HR_MANAGER+ |
| `/payroll/:id` | 급여 명세서 | 본인 or HR_MANAGER+ |
| `/my-payroll` | 내 급여 내역 | 전체 |

---

## 설계 원칙

- **금액 필드** — `DecimalField(max_digits=15, decimal_places=2)` 통일, `FloatField` 금지
- **삭제** — 소프트 삭제(`is_active=False`)만 허용 (한국 노동법 임금 이력 보존)
- **API 응답** — `{"success": bool, "data": ..., "message": ""}` 형식 통일
- **권한** — 모든 View에 `permission_classes` 명시
