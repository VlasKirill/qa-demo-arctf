# Demo Application (SUT)

Упрощенное демо-приложение для тестирования. Реализует систему регистрации и авторизации.

## Endpoints

- POST /register - регистрация пользователя
- POST /login - авторизация, возвращает JWT токен
- GET /me - получение информации о текущем пользователе (требует токен)
- GET /health - проверка работоспособности API

## Запуск

```bash
docker-compose up -d

## Отчеты о тестировании

Проект включает комплексное тестирование с использованием Allure Report для визуализации результатов.

### API-тесты (Pytest)
![API Tests Overview](docs/screenshots/allure-api-overview.png)

**Результаты:**
- Все API-тесты проходят успешно
- Покрытие: регистрация, авторизация, защищенные эндпоинты
- Включает позитивные, негативные сценарии и граничные значения

### UI E2E-тесты (Playwright)
![UI Tests Overview](docs/screenshots/allure-ui-overview.png)

**Результаты:**
- Все E2E-тесты проходят успешно
- Покрытие критических пользовательских сценариев
- Автоматические скриншоты на каждом шаге

### Детальный отчет
![Test Details](docs/screenshots/allure-test-details.png)

Allure-отчеты содержат:
- Пошаговое выполнение тестов
- Скриншоты UI на каждом этапе
- Логи API-запросов и ответов
- Вложения с JWT-токенами и данными

### Структура тестов
![Test Structure](docs/screenshots/allure-behaviors.png)

Тесты организованы по функциональности:
- **Registration** - тесты регистрации пользователей
- **Login** - тесты авторизации и JWT-токенов
- **Protected Endpoints** - тесты защищенных ресурсов
- **Validation** - тесты валидации данных

## Запуск тестов

### API-тесты
```bash
cd tests
pytest api/ -v --alluredir=allure-results-api
allure generate allure-results-api -o allure-report-api --clean
allure open allure-report-api

### UI-тесты
```bash
cd tests
pytest ui/ -v --alluredir=allure-results-ui
allure generate allure-results-ui -o allure-report-ui --clean
allure open allure-report-ui