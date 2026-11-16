from playwright.sync_api import Page
import allure

class BasePage:
    """
    Базовый класс для всех Page Objects.
    
    Что такое Page Object:
    - Это паттерн проектирования для UI-тестов
    - Каждая страница приложения представлена классом
    - Класс содержит локаторы элементов и методы взаимодействия
    
    Зачем использую:
    1. Переиспользование кода (не дублируем локаторы)
    2. Читаемость тестов (page.login() вместо page.fill("#email", ...))
    3. Легкость поддержки (изменился локатор- менять в одном месте)
    4. Абстракция (тесты не знают про HTML-структуру)
    
    Как использовать:
    class LoginPage(BasePage):
        EMAIL_INPUT = "#email"
        
        def fill_email(self, email):
            self.page.fill(self.EMAIL_INPUT, email)
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:3000"
    
    def navigate(self):
        """
        Переход на страницу.
        
        Зачем отдельный метод:
        - Инкапсуляция URL (не хардкодим в тестах)
        - Можно добавить ожидание загрузки
        - Легко изменить URL в одном месте
        """
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")
    
    def wait_for_element(self, selector: str, timeout: int = 5000):
        """
        Ожидание появления элемента на странице.
        
        Зачем ждать:
        - Страница загружается асинхронно
        - Элемент может появиться не сразу
        - Без ожидания тест может упасть с ошибкой "element not found"
        
        timeout: максимальное время ожидания в миллисекундах
        """
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def take_screenshot(self, name: str):
        """
        Создание скриншота для отчета в Allure.
        
        Зачем скриншоты:
        - Визуальное доказательство работы теста
        - Помогает при отладке упавших тестов
        - Красиво смотрится в отчете
        
        Как использовать:
        self.take_screenshot("login_form")
        """
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
    
    def get_text(self, selector: str) -> str:
        """Получить текст элемента"""
        return self.page.text_content(selector)
    
    def is_visible(self, selector: str) -> bool:
        """Проверить, виден ли элемент"""
        return self.page.is_visible(selector)