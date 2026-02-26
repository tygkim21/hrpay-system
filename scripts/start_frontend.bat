@echo off
echo ============================================================
echo  [Frontend] 프로덕션 서버 시작 (port 3000)
echo  URL: http://0.0.0.0:3000
echo ============================================================

cd /d %~dp0..\frontend

if not exist build (
    echo [오류] build 폴더가 없습니다. 먼저 build_frontend.bat 을 실행하세요.
    pause
    exit /b 1
)

npx serve -s build -l 3000

pause
