import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
import jwt

# Импортируем тестируемые функции напрямую из модуля
from app.backend.main import register, create_access_token, get_utc_now


class TestRegistrationMocks:
    
    def test_register_calls_send_email_directly(self, mocker, clean_db):
        """
        Проверяем вызов отправки email при прямом вызове функции (Unit-тест).
        
        Зачем: api_client общается с Docker-контейнером, а mocker.patch работает 
        только в локальном процессе Python. Чтобы протестировать мок, мы должны 
        вызвать функцию register напрямую, передав ей зависимости.
        """
        # 1. Мокаем функцию отправки email в локальном модуле
        mock_send_email = mocker.patch('app.backend.main.send_welcome_email')
        
        # 2. Создаем фейковый объект запроса (Pydantic модель)
        class FakeUser(BaseModel):
            email: EmailStr
            username: str
            password: str
            
        fake_user = FakeUser(email="test@example.com", username="testuser", password="TestPass123!")
        
        # 3. Вызываем функцию напрямую, передавая clean_db как зависимость (Depends)
        result = register(user=fake_user, db=clean_db)
        
        # 4. Проверяем результат выполнения
        assert result["message"] == "User registered successfully"
        
        # 5. Проверяем, что мок был вызван ровно 1 раз с правильным email
        mock_send_email.assert_called_once_with("test@example.com")


class TestTokenMocks:
    
    def test_token_expiration_logic(self, mocker):
        """
        Проверяем логику создания токена с правильным временем истечения.
        
        ЗАЧЕМ: Python 3.11+ запрещает патчить встроенный datetime.datetime напрямую.
        Мы обходим это, патча нашу собственную функцию-обертку get_utc_now().
        """
        # 1. Фиксируем время, ЯВНО указывая часовой пояс UTC
        fixed_now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # 2. Мокаем нашу функцию-помощник
        mocker.patch('app.backend.main.get_utc_now', return_value=fixed_now)
        
        # 3. Вызываем функцию создания токена
        token = create_access_token("test@example.com")
        
        # 4. Декодируем токен (без проверки подписи)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # 5. Проверяем, что время истечения (exp) ровно на 30 минут больше фиксированного
        expected_exp_dt = fixed_now + timedelta(minutes=30)
        expected_exp = int(expected_exp_dt.timestamp())
        
        assert payload["exp"] == expected_exp


class TestDatabaseLogicMocks:
    
    def test_register_duplicate_email_logic(self, mocker):
        """
        Проверяем логику обработки дубликата email БЕЗ реальной БД.
        (Этот тест уже работал, оставляем его как есть для полноты картины)
        """
        mock_db_connection = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_db_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 1, "email": "test@example.com"}
        
        mocker.patch('app.backend.main.get_db', return_value=mock_db_connection)
        
        class FakeUser(BaseModel):
            email: str
            username: str
            password: str
            
        fake_user = FakeUser(email="test@example.com", username="hacker", password="123")
        
        with pytest.raises(HTTPException) as exc_info:
            register(user=fake_user, db=mock_db_connection)
            
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"
        mock_db_connection.commit.assert_not_called()