@echo off
echo ============================================================
echo  인사보수시스템 전체 시작
echo  Backend : http://localhost:8000
echo  Frontend: http://localhost:3000
echo ============================================================

echo.
echo [1/2] Backend 서버 시작...
start "HR-Backend" cmd /k "call %~dp0start_backend.bat"

timeout /t 3 /nobreak > nul

echo [2/2] Frontend 서버 시작...
start "HR-Frontend" cmd /k "call %~dp0start_frontend.bat"

echo.
echo 서버 기동 완료. 브라우저에서 http://localhost:3000 접속하세요.
pause
