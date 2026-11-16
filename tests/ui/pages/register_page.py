from .base_page import BasePage
import allure

class RegisterPage(BasePage):
    """
    Page Object для страницы регистрации.
    
    Аналогичен LoginPage, но для формы регистрации.
    Содержит дополнительное поле username.
    """
    
    # Локаторы элементов
    
    EMAIL_INPUT = "#regEmail"
    USERNAME_INPUT = "#regUsername"
    PASSWORD_INPUT = "#regPassword"
    
    SUBMIT_BUTTON = "button:has-text('CREATE_ACCOUNT')"
    SWITCH_TO_LOGIN_TAB = "[data-tab='login']"
    
    MESSAGE = "#message"
    
    # Методы взаимодействия
    
    @allure.step("Заполнить поле email: {email}")
    def fill_email(self, email: str):
        self.page.fill(self.EMAIL_INPUT, email)
    
    @allure.step("Заполнить поле username: {username}")
    def fill_username(self, username: str):
        self.page.fill(self.USERNAME_INPUT, username)
    
    @allure.step("Заполнить поле password")
    def fill_password(self, password: str):
        self.page.fill(self.PASSWORD_INPUT, password)
    
    @allure.step("Нажать кнопку регистрации")
    def click_register_button(self):
        self.page.click(self.SUBMIT_BUTTON)
    
    @allure.step("Выполнить регистрацию: {email}, {username}")
    def register(self, email: str, username: str, password: str):
        """
        Полный сценарий регистрации.
        
        Объединяет заполнение всех полей и отправку формы.
        """
        self.fill_email(email)
        self.fill_username(username)
        self.fill_password(password)
        self.click_register_button()
    
    @allure.step("Переключиться на вкладку входа")
    def switch_to_login_tab(self):
        """Переключение на форму входа"""
        self.page.click(self.SWITCH_TO_LOGIN_TAB)
    
    # Методы проверки состояния
    
    @allure.step("Получить текст сообщения")
    def get_message_text(self) -> str:
        self.wait_for_element(self.MESSAGE)
        return self.get_text(self.MESSAGE)
    
    @allure.step("Проверить, что сообщение об успехе отображается")
    def is_success_message_visible(self) -> bool:
        return self.page.locator(self.MESSAGE).get_attribute("class").find("success") != -1
    
    @allure.step("Проверить, что сообщение об ошибке отображается")
    def is_error_message_visible(self) -> bool:
        return self.page.locator(self.MESSAGE).get_attribute("class").find("error") != -1
    
    @allure.step("Проверить, что форма очищена")
    def is_form_cleared(self) -> bool:
        """
        Проверка, что поля формы очищены после успешной регистрации.
        
        Зачем проверять:
        - UX-требование: после регистрации форма должна очиститься
        - Предотвращает случайную повторную отправку
        """
        email_value = self.page.input_value(self.EMAIL_INPUT)
        username_value = self.page.input_value(self.USERNAME_INPUT)
        password_value = self.page.input_value(self.PASSWORD_INPUT)
        
        return email_value == "" and username_value == "" and password_value == ""