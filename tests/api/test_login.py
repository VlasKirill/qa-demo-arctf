import pytest
import jwt
from datetime import datetime

class TestLoginSuccess:
    """Тесты успешной авторизации"""
    
    def test_login_success_returns_token(self, api_client, registered_user):
        """
        TC-003: Успешная авторизация возвращает JWT-токен
        
        Что проверяем:
        1. Статус-код 200
        2. Ответ содержит access_token
        3. Токен имеет правильную структуру (3 части через точки)
        4. Токен можно декодировать
        5. Payload содержит sub (email пользователя)
        6. Payload содержит exp (время истечения)
        """
        # Act: логинимся
        response = api_client.login(
            registered_user["email"],
            registered_user["password"]
        )
        
        # Assert: статус-код
        assert response.status_code == 200
        
        # Assert: структура ответа
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Assert: структура токена
        token = data["access_token"]
        parts = token.split(".")
        assert len(parts) == 3, "JWT should have 3 parts: header.payload.signature"
        
        # Assert: декодируем payload (без проверки подписи)
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "sub" in payload
        assert payload["sub"] == registered_user["email"]
        assert "exp" in payload
    
    def test_login_returns_user_info(self, api_client, registered_user):
        """
        Проверка, что ответ содержит информацию о пользователе.
        """
        response = api_client.login(
            registered_user["email"],
            registered_user["password"]
        )
        
        data = response.json()
        assert "user" in data
        
        user = data["user"]
        assert user["email"] == registered_user["email"]
        assert user["username"] == registered_user["username"]
        
        # Важно: пароль не должен возвращаться
        assert "password" not in user
        assert "password_hash" not in user

class TestLoginNegative:
    """Тесты негативных сценариев авторизации"""
    
    def test_login_nonexistent_user_returns_401(self, api_client, clean_db):
        """
        Попытка входа несуществующего пользователя.
        
        Почему 401, а не 404:
        - 404 раскрывает информацию о существовании пользователей
        - 401 с общим сообщением "Invalid credentials" безопаснее
        """
        response = api_client.login(
            "nonexistent@example.com",
            "TestPass123!"
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_wrong_password_returns_401(self, api_client, registered_user):
        """
        Попытка входа с неверным паролем.
        """
        response = api_client.login(
            registered_user["email"],
            "WrongPassword123!"
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    @pytest.mark.parametrize("email,password,expected_status", [
        ("", "TestPass123!", 422),           # пустой email -> 422 (ошибка валидации Pydantic)
        ("test@example.com", "", 401),       # пустой пароль -> 401 (Invalid credentials)
        ("", "", 422),                       # оба пустые -> 422 (ошибка валидации Pydantic)
    ])
    def test_login_empty_fields_returns_expected(self, api_client, email, password, expected_status):
        """
        Тестирование пустых полей через параметризацию.
        """
        response = api_client.login(email, password)
        assert response.status_code == expected_status

# Тесты защищенных эндпоинтов (/me)

class TestProtectedEndpoints:
    """Тесты эндпоинта /me с различными токенами"""
    
    def test_me_with_valid_token_returns_200(self, api_client, auth_token, registered_user):
        """
        Доступ к /me с валидным токеном.
        
        Что проверяем:
        1. Статус-код 200
        2. Возвращаются данные текущего пользователя
        3. Email совпадает с тем, что в токене
        """
        response = api_client.get_me(auth_token)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["username"] == registered_user["username"]
    
    def test_me_without_token_returns_401(self, api_client):
        """
        Доступ к /me без токена.
        """
        response = api_client.session.get(f"{api_client.base_url}/me")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    def test_me_with_invalid_token_returns_401(self, api_client):
        """
        Доступ к /me с невалидным токеном.
        """
        response = api_client.session.get(
            f"{api_client.base_url}/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_me_with_wrong_scheme_returns_401(self, api_client, auth_token):
        """
        Доступ к /me с неправильной схемой авторизации (не Bearer).
        """
        response = api_client.session.get(
            f"{api_client.base_url}/me",
            headers={"Authorization": f"Token {auth_token}"}  # Должно быть Bearer
        )
        
        assert response.status_code == 401
        assert "Invalid authorization scheme" in response.json()["detail"]
    
    def test_me_with_modified_payload_returns_401(self, api_client, auth_token):
        """
        Попытка подменить payload токена.
        
        Что проверяем:
        - Подпись JWT валидируется
        - Измененный токен отклоняется
        """
        # Декодируем оригинальный токен
        payload = jwt.decode(auth_token, options={"verify_signature": False})
        
        # Меняем email в payload
        payload["sub"] = "admin@example.com"
        
        # Кодируем обратно (без правильной подписи)
        modified_token = jwt.encode(
            payload,
            "wrong-secret-key",
            algorithm="HS256"
        )
        
        response = api_client.get_me(modified_token)
        
        # Должен отклонить из-за невалидной подписи
        assert response.status_code == 401