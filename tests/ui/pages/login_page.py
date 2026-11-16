from .base_page import BasePage
import allure

class LoginPage(BasePage):
    """
    Page Object для страницы авторизации.
    
    Что содержит:
    - Локаторы всех элементов формы логина
    - Методы взаимодействия с формой
    - Методы проверки состояния страницы
    
    Как определять локаторы:
    1. Открой DevTools (F12)
    2. Выбери элемент (инструмент "Inspect")
    3. Посмотри HTML-код элемента
    4. Выбери уникальный селектор:
       - ID: #loginEmail (самый надежный)
       - Class: .form-input (менее надежный)
       - Data-атрибут: [data-testid="email"] (рекомендуется)
       - XPath: //input[@type="email"] (последний вариант)
    
    Приоритет локаторов:
    1. data-testid (специально для тестов)
    2. ID (#elementId)
    3. ARIA-роли (role="button")
    4. CSS-селекторы (.class, [attribute])
    5. XPath (самый хрупкий)
    """
    
    # Локаторы элементов
    
    # Локаторы полей ввода
    EMAIL_INPUT = "#loginEmail"
    PASSWORD_INPUT = "#loginPassword"
    
    # Локаторы кнопок
    SUBMIT_BUTTON = "button:has-text('AUTHENTICATE')"
    SWITCH_TO_REGISTER_TAB = "[data-tab='register']"
    
    # Локаторы сообщений
    MESSAGE = "#message"
    STATUS_BAR = ".status-bar"
    API_STATUS = "#apiStatus"
    
    # Методы взаимодействия
    
    @allure.step("Заполнить поле email: {email}")
    def fill_email(self, email: str):
        """
        Заполнение поля email.
        
        @allure.step- декоратор для красивого отчета Allure
        """
        self.page.fill(self.EMAIL_INPUT, email)
    
    @allure.step("Заполнить поле password")
    def fill_password(self, password: str):
        """
        Заполнение поля password.
        
        Не логировать сам пароль в отчете.
        """
        self.page.fill(self.PASSWORD_INPUT, password)
    
    @allure.step("Нажать кнопку входа")
    def click_login_button(self):
        """Нажатие кнопки отправки формы"""
        self.page.click(self.SUBMIT_BUTTON)
    
    @allure.step("Выполнить вход с email: {email}")
    def login(self, email: str, password: str):
        """
        Полный сценарий входа.
        
        Зачем отдельный метод:
        - Объединяет несколько действий в одно
        - Тесты становятся чище: page.login() вместо 3 строк кода
        - Легко переиспользовать в разных тестах
        """
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()
    
    @allure.step("Переключиться на вкладку регистрации")
    def switch_to_register_tab(self):
        """Переключение на форму регистрации"""
        self.page.click(self.SWITCH_TO_REGISTER_TAB)
    
    # Методы проверки состояния
    
    @allure.step("Получить текст сообщения")
    def get_message_text(self) -> str:
        """Получить текст сообщения об успехе/ошибке"""
        self.wait_for_element(self.MESSAGE)
        return self.get_text(self.MESSAGE)
    
    @allure.step("Проверить, что сообщение об успехе отображается")
    def is_success_message_visible(self) -> bool:
        """Проверка отображения зеленого сообщения"""
        return self.page.locator(self.MESSAGE).get_attribute("class").find("success") != -1
    
    @allure.step("Проверить, что сообщение об ошибке отображается")
    def is_error_message_visible(self) -> bool:
        """Проверка отображения красного сообщения"""
        return self.page.locator(self.MESSAGE).get_attribute("class").find("error") != -1
    
    @allure.step("Проверить статус API")
    def get_api_status(self) -> str:
        """Получить статус API (ONLINE/OFFLINE)"""
        return self.get_text(self.API_STATUS)
    
    @allure.step("Проверить, что API онлайн")
    def is_api_online(self) -> bool:
        """Проверка, что API доступен"""
        status = self.get_api_status()
        return status == "ONLINE"