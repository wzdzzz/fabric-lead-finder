# Admin Panel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a web admin panel (FastAPI + React + SQLite) for the fabric lead finder tool.

**Architecture:** FastAPI backend wraps existing scraper/exporter modules, exposes REST API with JWT auth. React + Ant Design frontend provides management UI. SQLite via SQLAlchemy for persistence.

**Tech Stack:** Python (FastAPI, SQLAlchemy, PyJWT, uvicorn), React 18, TypeScript, Ant Design 5, Vite

---

### Task 1: Backend - Database & Models

**Files:**
- Create: `server/__init__.py`
- Create: `server/database.py`
- Create: `server/models.py`

Setup SQLAlchemy with SQLite, define Lead and ScrapeTask models.

---

### Task 2: Backend - Schemas & Auth

**Files:**
- Create: `server/schemas.py`
- Create: `server/auth.py`

Pydantic schemas for all request/response models. JWT auth with fixed credentials from config.

---

### Task 3: Backend - API Routers

**Files:**
- Create: `server/routers/__init__.py`
- Create: `server/routers/auth.py`
- Create: `server/routers/leads.py`
- Create: `server/routers/tasks.py`
- Create: `server/routers/export.py`

All REST endpoints as designed.

---

### Task 4: Backend - Scraper & Export Services

**Files:**
- Create: `server/services/__init__.py`
- Create: `server/services/scraper.py`
- Create: `server/services/export.py`

Wrap existing scraper_map.search_amap and exporter.export_to_excel for async task execution.

---

### Task 5: Backend - App Entry Point

**Files:**
- Create: `server/app.py`
- Modify: `requirements.txt`

FastAPI app with CORS, router registration, static file serving.

---

### Task 6: Frontend - Project Setup

**Files:**
- Create: `web/package.json`
- Create: `web/vite.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/index.html`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/api/client.ts`

React + Vite + Ant Design + React Router scaffold.

---

### Task 7: Frontend - Login Page

**Files:**
- Create: `web/src/pages/Login.tsx`

Simple login form with Ant Design.

---

### Task 8: Frontend - Dashboard Page

**Files:**
- Create: `web/src/pages/Dashboard.tsx`

Stats cards + scrape task launcher + task progress.

---

### Task 9: Frontend - Leads Page

**Files:**
- Create: `web/src/pages/Leads.tsx`

Data table with search, filter, inline edit status/tags, batch operations, export.

---

### Task 10: Frontend - History Page

**Files:**
- Create: `web/src/pages/History.tsx`

Scrape task history table.

---

### Task 11: Integration & Config Update

**Files:**
- Modify: `config.py` (add admin credentials, JWT secret)
- Create: `start.py` (one-command startup script)

Final wiring, production build serving, startup script.
