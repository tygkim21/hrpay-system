# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

인사보수시스템 (HR & Payroll System) — an integrated employee information and payroll management system. Backend: Django 4.2 + DRF. Frontend: React 19 (Create React App). Database: MariaDB. Currently in Phase 0-2 of development.

## Commands

### Backend
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run development server
python manage.py runserver 8000

# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Run Django tests
python manage.py test apps.<appname>

# Run a single test
python manage.py test apps.accounts.tests.TestClassName.test_method_name
```

### Frontend (from `frontend/` directory)
```bash
cd frontend

npm start        # Dev server on port 3000
npm test         # Run tests (interactive watch mode)
npm test -- --watchAll=false  # Run tests once (CI mode)
npm run build    # Production build
```

## Architecture

### Backend (`/apps/`)
Django project with four apps under `apps/`:

- **accounts** — Only fully implemented app. `CustomUser` model with `role` field (ADMIN/HR_MANAGER/EMPLOYEE). JWT auth via `/api/v1/auth/` endpoints (login, logout, refresh, me). Four permission classes in `permissions.py`: `IsAdmin`, `IsHRManager`, `IsEmployee`, `IsOwnerOrHRManager`.
- **employees** — Stub, Phase 3.
- **attendance** — Stub, Phase 4.
- **payroll** — Stub, Phase 5.

Django project configuration lives in `config/` (settings, urls, wsgi, asgi).

**API response format** — all endpoints must return:
```json
{"success": true, "data": {...}, "message": ""}
```

### Frontend (`/frontend/src/`)
- **`api/axiosInstance.js`** — Central Axios client. Base URL: `http://localhost:8000/api/v1`. Request interceptor injects JWT Bearer token from localStorage. Response interceptor auto-refreshes on 401; on refresh failure, clears localStorage and redirects to `/login`.
- **`api/authApi.js`** — Auth-specific API calls.
- **`store/authStore.js`** — Zustand store for auth state.
- **`hooks/useAuth.js`** — Custom auth hook.
- **`pages/`** — Full page components.
- **`components/`** — Reusable UI components (Ant Design-based).

React Query manages server state; Zustand manages client/UI state.

### Key Design Rules
- **Monetary fields:** Always `DecimalField(max_digits=15, decimal_places=2)` — never `FloatField`.
- **Deletion:** Soft-delete only (`is_active=False`). Korean labor law requires wage history preservation.
- **Permissions:** Every API view must declare explicit `permission_classes`.
- **URL routing:** All API endpoints under `/api/v1/`. New app URLs added to `config/urls.py`.

### Database
MariaDB configured via `.env`. Connection: host `127.0.0.1`, port `3306`, db `hrpay_db`, user `hrpay_user`. PyMySQL used as the DB driver (configured in `config/__init__.py`).

### JWT Configuration
Access token lifetime: 30 minutes. Refresh token lifetime: 7 days. Token blacklisting is enabled (`rest_framework_simplejwt.token_blacklist` in INSTALLED_APPS).
