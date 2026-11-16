import pytest
import requests
import sqlite3
from pathlib import Path

# Конфигурация путей

# __file__ - это путь к текущему файлу conftest.py
# .parent.parent поднимает нас из папки tests/ в корень проекта
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "app" / "backend" / "demo.db"

@pytest.fixture(scope="session")
def api_url():
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def frontend_url():
    return "http://localhost:3000"

# Фикстуры для работы с базой данных

@pytest.fixture(scope="function")
def db_connection():
    """Подключение к тестовой базе данных по абсолютному пути"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def clean_db(db_connection):
    """Очистка БД перед каждым тестом для полной изоляции"""
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM users")
    db_connection.commit()
    yield db_connection

# Фисктуры для API-тестов

@pytest.fixture
def api_client(api_url):
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.session = requests.Session()
        
        def register(self, email, username, password):
            return self.session.post(
                f"{self.base_url}/register",
                json={"email": email, "username": username, "password": password}
            )
        
        def login(self, email, password):
            return self.session.post(
                f"{self.base_url}/login",
                json={"email": email, "password": password}
            )
        
        def get_me(self, token):
            return self.session.get(
                f"{self.base_url}/me",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        def health_check(self):
            return self.session.get(f"{self.base_url}/health")
    
    return APIClient(api_url)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    }

@pytest.fixture
def registered_user(api_client, clean_db, test_user):
    response = api_client.register(
        test_user["email"],
        test_user["username"],
        test_user["password"]
    )
    assert response.status_code == 200, "Failed to register test user"
    return test_user

@pytest.fixture
def auth_token(api_client, registered_user):
    response = api_client.login(
        registered_user["email"],
        registered_user["password"]
    )
    assert response.status_code == 200
    return response.json()["access_token"]