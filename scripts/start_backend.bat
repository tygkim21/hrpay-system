@echo off
echo ============================================================
echo  [Backend] 인사보수시스템 — waitress 서버 시작
echo  URL: http://0.0.0.0:8000
echo ============================================================

cd /d %~dp0..

call .venv\Scripts\activate.bat

echo Django 시스템 점검 중...
python manage.py check --deploy 2>nul || python manage.py check

echo.
echo 정적 파일 수집 중...
python manage.py collectstatic --noinput

echo.
echo waitress 서버 실행 중 (port 8000)...
waitress-serve --host=0.0.0.0 --port=8000 --threads=4 config.wsgi:application

pause
