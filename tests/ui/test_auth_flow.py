import pytest
import allure
import time
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from playwright.sync_api import expect

@allure.epic("Auth Demo Application")
@allure.feature("Authentication Flow")
class TestAuthFlow:
    """
    E2E тесты полного пользовательского сценария.
    
    Что такое E2E (End-to-End) тесты:
    - Тестируют полный сценарий от начала до конца
    - Имитируют реальные действия пользователя
    - Проверяют взаимодействие всех компонентов (frontend + backend + DB)
    
    Отличия от API-тестов:
    - API-тесты: быстрые, проверяют логику backend
    - E2E-тесты: медленные, проверяют UX и интеграцию
    
    Когда использую:
    - Критические пользовательские сценарии (регистрация, оплата)
    - Проверка UI-логики (валидация, сообщения)
    - Интеграционное тестирование (frontend + backend)
    """
    
    @allure.story("Registration and Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Полный сценарий: регистрация и вход")
    def test_full_registration_and_login_flow(self, page):
        """
        TC-UI-001: Полный сценарий регистрации и входа
        
        Что проверяю:
        1. Пользователь может зарегистрироваться
        2. После регистрации появляется сообщение об успехе
        3. Пользователь может переключиться на вкладку входа
        4. Пользователь может войти с созданными credentials
        5. После входа появляется приветственное сообщение
        6. Токен сохраняется в localStorage
        
        Почему это критический тест:
        - Это основной пользовательский сценарий
        - Если он не работает, приложение бесполезно
        - Должен проходить в каждом релизе
        """
        # Arrange: создаем Page Objects
        register_page = RegisterPage(page)
        login_page = LoginPage(page)
        
        # Тестовые данные
        test_email = f"e2e_test_{int(time.time())}@example.com"
        test_username = "e2e_user"
        test_password = "E2ETestPass123!"
        
        with allure.step("Шаг 1: Переход на страницу регистрации"):
            register_page.navigate()
            register_page.page.click("[data-tab='register']")
            register_page.take_screenshot("01_initial_page")
        
        with allure.step("Шаг 2: Заполнение формы регистрации"):
            register_page.register(test_email, test_username, test_password)
            register_page.take_screenshot("02_registration_submitted")
        
        with allure.step("Шаг 3: Проверка сообщения об успешной регистрации"):
            # Ждем появление текста в элементе
            expect(page.locator("#message")).to_contain_text("Registration successful", timeout=10000)

            message = register_page.get_message_text()
            assert "Registration successful" in message, \
                f"Expected success message, got: {message}"
            assert register_page.is_success_message_visible(), \
                "Success message should be green"
            register_page.take_screenshot("03_registration_success")
        
        with allure.step("Шаг 4: Проверка очистки формы"):
            assert register_page.is_form_cleared(), \
                "Form should be cleared after successful registration"
        
        with allure.step("Шаг 5: Переключение на вкладку входа"):
            register_page.switch_to_login_tab()
            login_page.take_screenshot("04_switched_to_login")
        
        with allure.step("Шаг 6: Выполнение входа"):
            login_page.login(test_email, test_password)
            login_page.take_screenshot("05_login_submitted")
        
        with allure.step("Шаг 7: Проверка приветственного сообщения"):
            # Ждем сообщение
            expect(page.locator("#message")).to_contain_text("Welcome", timeout=10000)
            
            message = login_page.get_message_text()
            assert f"Welcome, {test_username}" in message, \
                f"Expected welcome message with username, got: {message}"
            assert login_page.is_success_message_visible(), \
                "Welcome message should be green"
            login_page.take_screenshot("06_login_success")
        
        with allure.step("Шаг 8: Проверка сохранения токена в localStorage"):
            token = page.evaluate("localStorage.getItem('token')")
            assert token is not None, "Token should be saved in localStorage"
            assert token.startswith("eyJ"), \
                "Token should be a valid JWT (starts with 'eyJ')"
            
            # Логируем токен в Allure (безопасно, это тестовый токен)
            allure.attach(
                token,
                name="JWT Token",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("Registration Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Регистрация с существующим email")
    def test_registration_with_duplicate_email(self, page):
        """
        TC-UI-002: Попытка регистрации с уже существующим email
        
        Что проверяем:
        1. Первый пользователь регистрируется успешно
        2. Второй пользователь с тем же email получает ошибку
        3. Сообщение об ошибке информативное
        """
        register_page = RegisterPage(page)
        register_page.navigate()
        register_page.page.click("[data-tab='register']")

        # Генерируем уникальный email для этого запуска теста
        unique_email = f"duplicate_{int(time.time())}@example.com"
        
        # Первая регистрация
        register_page.register(
            unique_email,
            "user1",
            "Pass123!"
        )
        
        # Ждем появления сообщения об успехе
        expect(page.locator("#message")).to_contain_text("Registration successful", timeout=10000)
        
        register_page.register(
            unique_email,  # тот же email
            "user2",
            "Pass456!"
        )
        
        # Ждем появления ошибки
        expect(page.locator("#message")).to_contain_text("already registered", timeout=10000)
        
        # Проверка ошибки
        message = register_page.get_message_text()
        assert "already registered" in message.lower(), \
            f"Expected 'already registered' error, got: {message}"
        assert register_page.is_error_message_visible(), \
            "Error message should be red"
    
    @allure.story("Login Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Вход с неверным паролем")
    def test_login_with_wrong_password(self, page):
        """
        TC-UI-003: Попытка входа с неверным паролем
        
        Что проверяем:
        1. Пользователь регистрируется
        2. Пытается войти с неверным паролем
        3. Получает ошибку "Invalid credentials"
        4. Токен НЕ сохраняется в localStorage
        """
        register_page = RegisterPage(page)
        login_page = LoginPage(page)
        
        # Регистрация
        register_page.navigate()
        register_page.page.click("[data-tab='register']")

        # Генерируем уникальный email
        unique_email = f"test_{int(time.time())}@example.com"
        
        register_page.register(
            unique_email,
            "testuser",
            "CorrectPass123!"
        )
        
        # Ждем успеха
        expect(page.locator("#message")).to_contain_text("Registration successful", timeout=10000)
        
        # Переключение на вход
        register_page.switch_to_login_tab()
        
        # Попытка входа с неверным паролем
        login_page.login(
            unique_email,
            "WrongPassword123!"  # неверный пароль
        )
        
        # Ждем появления ошибки
        expect(page.locator("#message")).to_contain_text("Invalid credentials", timeout=10000)
        
        # Проверка ошибки
        message = login_page.get_message_text()
        assert "Invalid credentials" in message, \
            f"Expected 'Invalid credentials' error, got: {message}"
        assert login_page.is_error_message_visible(), \
            "Error message should be red"
        
        # Проверка, что токен НЕ сохранен
        token = page.evaluate("localStorage.getItem('token')")
        assert token is None, \
            "Token should NOT be saved after failed login"
    
    @allure.story("Client-side Validation")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Клиентская валидация пустых полей")
    def test_empty_fields_validation(self, page):
        """
        TC-UI-004: Валидация пустых полей на клиенте
        
        Что проверяем:
        1. Браузер не отправляет запрос при пустых полях
        2. Срабатывает HTML5-валидация (required)
        3. Пользователь видит подсказку заполнить поле
        """
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Пытаемся отправить пустую форму
        login_page.click_login_button()
        
        # Проверяем, что запрос НЕ был отправлен
        # (если бы был отправлен, появилось бы сообщение от сервера)
        message = login_page.get_message_text()
        assert message == "" or message is None, \
            "No request should be sent for empty form"
        
        # Проверяем, что поля имеют атрибут required
        email_required = page.get_attribute(LoginPage.EMAIL_INPUT, "required")
        password_required = page.get_attribute(LoginPage.PASSWORD_INPUT, "required")
        
        assert email_required is not None, "Email field should be required"
        assert password_required is not None, "Password field should be required"
    
    @allure.story("API Status Indicator")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Индикатор статуса API")
    def test_api_status_indicator(self, page):
        """
        TC-UI-005: Проверка индикатора статуса API
        
        Что проверяю:
        1. При работающем API отображается "ONLINE"
        2. Индикатор зеленого цвета
        """
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Ждем, пока индикатор обновится
        page.wait_for_timeout(1000)  # 1 секунда
        
        # Проверяем статус
        assert login_page.is_api_online(), \
            "API should be online when backend is running"
        
        # Проверяем цвет (зеленый)
        api_status_element = page.locator(LoginPage.API_STATUS)
        color = api_status_element.evaluate("el => getComputedStyle(el).color")
        
        # Зеленый цвет в RGB: rgb(0, 255, 136) или похожий
        assert "0" in color and "255" in color, \
            f"API status should be green, got color: {color}"