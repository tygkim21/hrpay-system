@echo off
echo ============================================================
echo  [Frontend] 프로덕션 빌드
echo ============================================================

cd /d %~dp0..\frontend

if not exist .env.production (
    echo [경고] frontend\.env.production 파일이 없습니다.
    echo        .env.production.example 을 복사하고 서버 IP를 입력하세요.
    echo        예: copy .env.production.example .env.production
    pause
    exit /b 1
)

echo npm 빌드 시작...
npm run build

echo.
echo 빌드 완료: frontend\build\ 폴더를 확인하세요.
pause
