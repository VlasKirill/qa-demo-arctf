# Bug report BR-002

**Title:** Ошибка 404 в логах backend на эндпоинте /health

**Severity:** Critical
**Priority:** High
**Status:** Fixed
**Found on:** 10.XX.2026
**Fixed on:** 10.XX.2026

**Environment:**
- Docker container: python:3.11-slim
- passlib==1.7.4
- bcrypt==4.0.1
- FastAPI 0.104.1

**Steps to reproduce:**
1. Запустить приложение через docker-compose up --build -d
2. Проверить логи backend
3. Проанализировать ответ сервера

**Actual result:**
Ответ от сервера 404 Not Found на эндпоинте /health

**Expected result:**
Ответ на эндпоинте /health 200 OK

**Root cause:**
В файле app/backend/main.py не был прописан эндпоинт /health в следствии фикса BR-001

**Proposed solution:**
-Добавить эндпоинт /health в main.py

**Applied fix:**
- В main.py добавлен эндпоинт /health