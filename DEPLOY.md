# 배포 체크리스트 — 인사보수시스템

> **대상 환경**: Windows Server · MariaDB 11.3 · Python 3.12 · Node.js 18+
> **아키텍처**: waitress (Django, port 8000) + serve (React build, port 3000)

---

## 사전 준비

### 서버 소프트웨어 확인
- [ ] Python 3.12 이상 설치 확인 → `python --version`
- [ ] Node.js 18 이상 설치 확인 → `node --version`
- [ ] MariaDB 11.3 실행 중 확인 → 서비스 관리자 또는 `mysql --version`
- [ ] Git 설치 확인 → `git --version`

### 소스 코드 준비
- [ ] 저장소 클론 (최초 1회)
  ```bat
  git clone https://github.com/tygkim21/hrpay-system.git
  cd hrpay-system
  ```
- [ ] 최신 코드 반영 (업데이트 시)
  ```bat
  git pull origin master
  ```

---

## 1단계 — 백엔드 환경 구성

### 가상환경 및 패키지
- [ ] 가상환경 생성 (최초 1회)
  ```bat
  python -m venv .venv
  ```
- [ ] 가상환경 활성화
  ```bat
  .venv\Scripts\activate
  ```
- [ ] 패키지 설치
  ```bat
  pip install -r requirements.txt
  ```
- [ ] waitress, whitenoise 포함 여부 확인
  ```bat
  pip show waitress whitenoise
  ```

### 환경변수 설정
- [ ] `.env` 파일 생성 (`.env.example` 복사 후 수정)
  ```bat
  copy .env.example .env
  ```
- [ ] `.env` 필수 항목 설정

  | 항목 | 운영값 예시 | 주의 |
  |------|------------|------|
  | `SECRET_KEY` | 50자 이상 랜덤 문자열 | **절대 공유 금지** |
  | `DEBUG` | `False` | 운영에서 반드시 False |
  | `ALLOWED_HOSTS` | `192.168.0.100,localhost` | 서버 IP 포함 |
  | `DB_NAME` | `hrpay_db` | |
  | `DB_USER` | `hrpay_user` | |
  | `DB_PASSWORD` | (실제 비밀번호) | |
  | `DB_HOST` | `127.0.0.1` | |
  | `DB_PORT` | `3306` | |
  | `CORS_ALLOWED_ORIGINS` | `http://192.168.0.100:3000` | 프론트 URL |

- [ ] SECRET_KEY 생성 (Python으로 직접 생성)
  ```bat
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

### 데이터베이스
- [ ] MariaDB에 DB·유저 생성 (최초 1회)
  ```sql
  CREATE DATABASE hrpay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER 'hrpay_user'@'localhost' IDENTIFIED BY '비밀번호';
  GRANT ALL PRIVILEGES ON hrpay_db.* TO 'hrpay_user'@'localhost';
  GRANT ALL PRIVILEGES ON test_hrpay_db.* TO 'hrpay_user'@'localhost';
  FLUSH PRIVILEGES;
  ```
- [ ] DB 접속 확인
  ```bat
  python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('DB OK')"
  ```
  > 실행 전 `set DJANGO_SETTINGS_MODULE=config.settings` 또는 가상환경 내에서 실행

- [ ] 마이그레이션 적용
  ```bat
  python manage.py migrate
  ```
- [ ] 마이그레이션 상태 확인 (미적용 항목 없어야 함)
  ```bat
  python manage.py showmigrations
  ```

### Django 점검
- [ ] 시스템 점검
  ```bat
  python manage.py check
  ```
- [ ] 배포 점검 (경고 항목 검토)
  ```bat
  python manage.py check --deploy
  ```
- [ ] 관리자 계정 생성 (최초 1회)
  ```bat
  python manage.py createsuperuser
  ```
- [ ] 정적 파일 수집
  ```bat
  python manage.py collectstatic --noinput
  ```
  → `staticfiles/` 폴더에 수집됨

---

## 2단계 — 프론트엔드 빌드

- [ ] `frontend/.env.production` 생성
  ```bat
  copy frontend\.env.production.example frontend\.env.production
  ```
- [ ] `frontend/.env.production` 내 API URL 수정
  ```
  REACT_APP_API_URL=http://192.168.0.100:8000/api/v1
  ```
  > `192.168.0.100` 자리에 실제 서버 IP 입력

- [ ] npm 패키지 설치
  ```bat
  cd frontend
  npm install
  cd ..
  ```
- [ ] 프로덕션 빌드 실행
  ```bat
  scripts\build_frontend.bat
  ```
- [ ] `frontend\build\` 폴더 생성 확인
  ```bat
  dir frontend\build
  ```

---

## 3단계 — 서버 기동

### 백엔드 + 프론트엔드 동시 시작
```bat
scripts\start_all.bat
```

### 개별 기동 (문제 진단 시)
```bat
:: 백엔드만
scripts\start_backend.bat

:: 프론트엔드만
scripts\start_frontend.bat
```

---

## 4단계 — 동작 확인

### 백엔드 API 확인
- [ ] 헬스체크 응답 확인
  ```
  GET http://서버IP:8000/api/v1/health/
  → {"success": true, "data": null, "message": "서버 정상 동작 중"}
  ```
- [ ] 로그인 API 동작 확인
  ```
  POST http://서버IP:8000/api/v1/auth/login/
  Body: {"username": "admin", "password": "..."}
  → access, refresh 토큰 반환
  ```
- [ ] Django 관리자 페이지 접속 확인
  ```
  http://서버IP:8000/admin/
  ```

### 프론트엔드 확인
- [ ] 브라우저에서 접속 확인
  ```
  http://서버IP:3000
  ```
- [ ] 로그인 후 직원 목록 조회 확인
- [ ] 급여 계산 → 확정 → 급여대장 PDF 출력 흐름 확인

### 네트워크
- [ ] 방화벽 포트 개방 확인 (Windows Defender 방화벽)
  - `8000` (백엔드 API)
  - `3000` (프론트엔드)
  ```bat
  netsh advfirewall firewall add rule name="HR-Backend" dir=in action=allow protocol=TCP localport=8000
  netsh advfirewall firewall add rule name="HR-Frontend" dir=in action=allow protocol=TCP localport=3000
  ```

---

## 5단계 — 서비스 자동 시작 설정 (선택)

서버 재부팅 후 자동으로 시작되게 하려면 **NSSM** (Non-Sucking Service Manager) 사용을 권장합니다.

```bat
:: NSSM으로 백엔드를 Windows 서비스로 등록
nssm install HR-Backend "C:\hrpay-system\scripts\start_backend.bat"
nssm start HR-Backend

:: NSSM으로 프론트엔드를 Windows 서비스로 등록
nssm install HR-Frontend "C:\hrpay-system\scripts\start_frontend.bat"
nssm start HR-Frontend
```

---

## 업데이트 배포 절차

코드 변경 후 재배포 시:

```bat
:: 1. 최신 코드 받기
git pull origin master

:: 2. 패키지 변경 여부 확인 후 설치
pip install -r requirements.txt

:: 3. 마이그레이션 (모델 변경 시)
python manage.py migrate

:: 4. 프론트엔드 재빌드 (소스 변경 시)
scripts\build_frontend.bat

:: 5. 서버 재시작
::    (실행 중인 start_backend / start_frontend 창 닫고 재실행)
scripts\start_all.bat
```

---

## 롤백 절차

문제 발생 시:

```bat
:: 이전 커밋으로 되돌리기
git log --oneline -5          :: 되돌릴 커밋 해시 확인
git checkout <커밋해시> -- .  :: 해당 시점 파일 복원
pip install -r requirements.txt
python manage.py migrate
scripts\build_frontend.bat
scripts\start_all.bat
```

---

## 보안 점검 항목

- [ ] `.env` 파일이 Git에 올라가지 않았는지 확인 → `git status`에서 `.env` 미포함
- [ ] `DEBUG=False` 설정 확인
- [ ] `SECRET_KEY`가 기본값이 아닌 충분히 복잡한 값인지 확인 (50자 이상)
- [ ] `ALLOWED_HOSTS`에 불필요한 주소 없는지 확인
- [ ] DB 비밀번호가 충분히 강한지 확인
- [ ] `staticfiles/` 폴더가 Git에 포함되지 않았는지 확인

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `waitress-serve: command not found` | 가상환경 미활성화 | `.venv\Scripts\activate` 후 재실행 |
| DB 접속 오류 | .env DB 설정 오류 또는 MariaDB 미실행 | MariaDB 서비스 확인, .env 값 재확인 |
| CORS 오류 (브라우저) | `CORS_ALLOWED_ORIGINS` 미설정 | .env에 프론트 URL 추가 후 재시작 |
| 정적 파일 404 | `collectstatic` 미실행 | `python manage.py collectstatic --noinput` |
| 프론트 API 연결 실패 | `REACT_APP_API_URL` 오설정 | `.env.production` 수정 후 `npm run build` 재실행 |
| 포트 이미 사용 중 | 이전 프로세스 잔존 | 작업 관리자에서 해당 포트 프로세스 종료 |
