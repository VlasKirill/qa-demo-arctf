# Bug report BR-003

**Title:** Запрос на эндпоинт /me с токеном удаленного из БД юзера 200 OK.

**Severity:** High
**Priority:** High
**Status:** In work
**Found on:** 10.XX.2026
**Fixed on:** In work

**Environment:**
- Docker container: python:3.11-slim
- passlib==1.7.4
- bcrypt==4.0.1
- FastAPI 0.104.1
- SQLite3

**Conditions:**
Пользователь создан на эндпоинте :8000/register с корректными credentials.

**Steps to reproduce:**
1. Отправить запрос POST на эндпоинт :8000/login, получить 200 OK и токен.
2. Скопировать токен, отправить запрос GET на эндпоинт :8000/me в Authorization с токеном, 200 OK.
3. Удалить пользователя из БД.
4. Отправить повторный запрос с тем же токеном.

**Actual result:**
После запроса идет ответ 200 OK.

**Excepted result:**
В следствии удаления пользователя токен стал неаутентифицированным, ответ 401 Unauthorized.

**Root cause:**
В app/backend/main.py в эндпоинте /me нет соответствующей обработки.