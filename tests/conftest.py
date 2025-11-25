import pytest
import requests
import random
import time
from typing import Generator, Dict, Any, List

BASE_URL = "https://qa-internship.avito.com"
SELLER_ID_MIN = 111111
SELLER_ID_MAX = 999999

class APIClient:
    """Клиент для работы с API Avito."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def create_item(self, data: Dict[str, Any]) -> requests.Response:
        """Создание объявления POST /api/1/item"""
        return self.session.post(f"{self.base_url}/api/1/item", json=data)
    
    def get_item(self, item_id: str) -> requests.Response:
        """Получение объявления по ID GET /api/1/item/{id}"""
        return self.session.get(f"{self.base_url}/api/1/item/{item_id}")
    
    def get_seller_items(self, seller_id: int) -> requests.Response:
        """Получение всех объявлений продавца GET /api/1/{sellerID}/item"""
        return self.session.get(f"{self.base_url}/api/1/{seller_id}/item")
    
    def get_statistic(self, item_id: str) -> requests.Response:
        """Получение статистики объявления GET /api/1/statistic/{id}"""
        return self.session.get(f"{self.base_url}/api/1/statistic/{item_id}")
    
    def delete_item(self, item_id: str) -> requests.Response:
        """Удаление объявления DELETE /api/2/item/{id}"""
        return self.session.delete(f"{self.base_url}/api/2/item/{item_id}")


def generate_unique_seller_id() -> int:
    """Генерация уникального sellerID с использованием timestamp и random."""
    timestamp = int(time.time() * 1000) % 800000
    random_part = random.randint(0, 88888)
    return SELLER_ID_MIN + (timestamp + random_part) % 888888


def generate_random_seller_id() -> int:
    """Генерация случайного sellerID в допустимом диапазоне."""
    return random.randint(SELLER_ID_MIN, SELLER_ID_MAX)


def create_valid_item_data(seller_id: int = None, name: str = "Тестовый товар", 
                           price: int = 1000, likes: int = 0, 
                           view_count: int = 0, contacts: int = 0) -> Dict[str, Any]:
    """
    Создание валидных данных для объявления.
    
    ВАЖНО: Поля likes, viewCount, contacts должны быть на ВЕРХНЕМ уровне JSON!
    Это реальный формат API (расхождение с документацией Postman - см. BUG-001).
    """
    if seller_id is None:
        seller_id = generate_unique_seller_id()
    
    return {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "likes": likes,
        "viewCount": view_count,
        "contacts": contacts
    }

@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    """Фикстура для создания API клиента на всю сессию."""
    client = APIClient(BASE_URL)
    yield client


@pytest.fixture
def unique_seller_id() -> int:
    """Фикстура для генерации уникального sellerID."""
    return generate_unique_seller_id()


@pytest.fixture
def valid_item_data(unique_seller_id: int) -> Dict[str, Any]:
    """Фикстура для создания валидных данных объявления."""
    return create_valid_item_data(seller_id=unique_seller_id)


@pytest.fixture
def created_item(api_client: APIClient, unique_seller_id: int) -> Generator[Dict[str, Any], None, None]:
    """
    Фикстура для создания объявления и получения его данных.
    Возвращает данные созданного объявления.
    """
    item_data = create_valid_item_data(seller_id=unique_seller_id)
    response = api_client.create_item(item_data)
    
    assert response.status_code == 200, f"Не удалось создать объявление: {response.text}"
    
    created = response.json()
    created["_request_data"] = item_data
    
    yield created
    
    # Cleanup
    try:
        api_client.delete_item(created.get("id", ""))
    except Exception:
        pass


@pytest.fixture
def multiple_items(api_client: APIClient, unique_seller_id: int) -> Generator[List[Dict[str, Any]], None, None]:
    """Фикстура для создания нескольких объявлений одного продавца."""
    items = []
    
    for i in range(3):
        item_data = create_valid_item_data(
            seller_id=unique_seller_id,
            name=f"Товар {i+1}",
            price=1000 * (i + 1)
        )
        response = api_client.create_item(item_data)
        
        if response.status_code == 200:
            created = response.json()
            created["_request_data"] = item_data
            items.append(created)
    
    yield items
    
    # Cleanup
    for item in items:
        try:
            api_client.delete_item(item.get("id", ""))
        except Exception:
            pass

def pytest_configure(config):
    """Добавление маркеров."""
    config.addinivalue_line("markers", "positive: Позитивные тест-кейсы")
    config.addinivalue_line("markers", "negative: Негативные тест-кейсы")
    config.addinivalue_line("markers", "integration: Интеграционные тест-кейсы")
    config.addinivalue_line("markers", "smoke: Smoke тесты")
    config.addinivalue_line("markers", "boundary: Тесты граничных значений")
