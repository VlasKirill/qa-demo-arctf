# Bug report BR-001

**Title:** Ошибка 500 при регистрации/авторизации из-за несовместимости passlib и bcrypt 4.1+

**Severity:** Critical
**Priority:** High
**Status:** Fixed
**Found on:** 10.XX.2026
**Fixed on:** 10.XX.2026

**Environment:**
- Docker container: python:3.11-slim
- passlib==1.7.4
- bcrypt==4.2.0
- FastAPI 0.104.1

**Steps to reproduce:**
1. Запустить приложение через docker-compose up
2. Отправить POST /register с валидными данными
3. Получить и проанализировать ответ 

**Actual result:**
Приложение возвращает 500 Internal server error. В логах:
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary

Трейсбэк указывает на passlib/handlers/bcrypt.py:380 в функции detect_wrap_bug.

**Expected result:**
Успешная регистрация, ответ 200 OK с user_id.

**Root cause:**
passlib 1.7.4 при инициализации bcrypt-бэкенда выполняет проверку detect_wrap_bug, 
используя тестовый пароль длиннее 72 байт. Начиная с bcrypt 4.1, библиотека 
стала строго валидировать длину пароля и выбрасывает ValueError.

**Proposed solution:**
- Зафиксировать bcrypt<4.1.0 в requirements.txt
- Добавить параметр truncate_error=True в CryptContext для защиты от подобных проблем

**Applied Fix:**
- bcrypt зафиксирован на версии 4.0.1
- В main.py добавлен truncate_error=True

**Prevention:**
Добавить в CI-пайплайн проверку совместимости зависимостей (pip-audit) и 
покрытие тестами сценариев регистрации/авторизации в smoke-наборе.