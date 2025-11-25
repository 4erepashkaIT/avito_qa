"""
Тесты для API создания объявлений POST /api/1/item
Тест-кейсы: TC-001 — TC-016
"""
import pytest
from conftest import APIClient, create_valid_item_data, generate_unique_seller_id


class TestCreateItemPositive:
    """Позитивные тесты создания объявлений."""
    
    @pytest.mark.positive
    @pytest.mark.smoke
    def test_tc001_create_item_with_valid_data(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-001: Успешное создание объявления с валидными данными.
        
        Проверяет:
        - Код ответа 200 OK
        - Наличие всех обязательных полей в ответе
        - Соответствие данных запросу
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Тестовый товар",
            "price": 1000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        # Проверка структуры ответа
        assert "id" in data, "Поле 'id' отсутствует в ответе"
        assert data["id"], "Поле 'id' пустое"
        assert isinstance(data["id"], str), "Поле 'id' должно быть строкой"
        
        assert "sellerId" in data, "Поле 'sellerId' отсутствует в ответе"
        assert data["sellerId"] == unique_seller_id, f"sellerId не совпадает: ожидался {unique_seller_id}, получен {data['sellerId']}"
        
        assert "name" in data, "Поле 'name' отсутствует в ответе"
        assert data["name"] == "Тестовый товар", f"name не совпадает: ожидался 'Тестовый товар', получен {data['name']}"
        
        assert "price" in data, "Поле 'price' отсутствует в ответе"
        assert data["price"] == 1000, f"price не совпадает: ожидался 1000, получен {data['price']}"
        
        assert "statistics" in data, "Поле 'statistics' отсутствует в ответе"
        assert "createdAt" in data, "Поле 'createdAt' отсутствует в ответе"
        assert data["createdAt"], "Поле 'createdAt' пустое"
    
    @pytest.mark.positive
    @pytest.mark.boundary
    def test_tc002_create_item_with_zero_price(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-002: Создание объявления с минимальной ценой (0).
        
        Проверяет возможность создания бесплатного объявления.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Бесплатный товар",
            "price": 0,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert data["price"] == 0, f"price не совпадает: ожидался 0, получен {data['price']}"
    
    @pytest.mark.positive
    @pytest.mark.boundary
    def test_tc003_create_item_with_max_price(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-003: Создание объявления с максимальной ценой (INT32_MAX).
        
        Проверяет обработку граничного значения цены.
        """
        # Arrange
        max_price = 2147483647  # INT32_MAX
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Дорогой товар",
            "price": max_price,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert data["price"] == max_price, f"price не совпадает: ожидался {max_price}, получен {data['price']}"
    
    @pytest.mark.positive
    @pytest.mark.boundary
    def test_tc004_create_item_with_long_name(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-004: Создание объявления с длинным названием (1000 символов).
        
        Проверяет обработку длинных строк.
        """
        # Arrange
        long_name = "А" * 1000
        item_data = {
            "sellerID": unique_seller_id,
            "name": long_name,
            "price": 500,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        # Допускается как 200 OK, так и 400 Bad Request
        assert response.status_code in [200, 400], f"Ожидался статус 200 или 400, получен {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == long_name, "Длинное название не сохранено полностью"
    
    @pytest.mark.positive
    def test_tc005_create_item_with_special_characters(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-005: Создание объявления со специальными символами в названии.
        
        Проверяет корректную обработку спецсимволов.
        """
        # Arrange
        special_name = "Товар №1 <test> & \"quotes\" 'apostrophe' @#$%"
        item_data = {
            "sellerID": unique_seller_id,
            "name": special_name,
            "price": 1500,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert data["name"] == special_name, f"Специальные символы не сохранены: ожидалось '{special_name}', получено '{data['name']}'"
    
    @pytest.mark.positive
    def test_tc006_create_item_with_nonzero_statistics(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-006: Создание объявления с начальной статистикой больше нуля.
        
        Проверяет возможность указания начальной статистики.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Популярный товар",
            "price": 2000,
            "statistics": {
                "likes": 100,
                "viewCount": 500,
                "contacts": 25
            }
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        stats = data.get("statistics", {})
        
        assert stats.get("likes") == 100, f"likes не совпадает: ожидалось 100, получено {stats.get('likes')}"
        assert stats.get("viewCount") == 500, f"viewCount не совпадает: ожидалось 500, получено {stats.get('viewCount')}"
        assert stats.get("contacts") == 25, f"contacts не совпадает: ожидалось 25, получено {stats.get('contacts')}"


class TestCreateItemNegative:
    """Негативные тесты создания объявлений."""
    
    @pytest.mark.negative
    def test_tc007_create_item_without_name(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-007: Создание объявления без поля name.
        
        Проверяет валидацию обязательных полей.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "price": 1000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc008_create_item_without_price(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-008: Создание объявления без поля price.
        
        Проверяет валидацию обязательных полей.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар без цены",
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc009_create_item_without_seller_id(self, api_client: APIClient):
        """
        TC-009: Создание объявления без поля sellerID.
        
        Проверяет валидацию обязательных полей.
        """
        # Arrange
        item_data = {
            "name": "Товар без продавца",
            "price": 1000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc010_create_item_without_statistics(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-010: Создание объявления без поля statistics.
        
        Проверяет валидацию обязательных полей.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар без статистики",
            "price": 1000
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        # API может как принять запрос с дефолтной статистикой, так и вернуть 400
        assert response.status_code in [200, 400], f"Ожидался статус 200 или 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc011_create_item_with_negative_price(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-011: Создание объявления с отрицательной ценой.
        
        Проверяет валидацию цены.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар с отрицательной ценой",
            "price": -100,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc012_create_item_with_negative_statistics(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-012: Создание объявления с отрицательной статистикой.
        
        Проверяет валидацию значений статистики.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар",
            "price": 1000,
            "statistics": {
                "likes": -10,
                "viewCount": -5,
                "contacts": -3
            }
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc013_create_item_with_string_price(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-013: Создание объявления с неверным типом данных для price (строка).
        
        Проверяет валидацию типов данных.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар",
            "price": "тысяча рублей",
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc014_create_item_with_string_seller_id(self, api_client: APIClient):
        """
        TC-014: Создание объявления с неверным типом данных для sellerID (строка).
        
        Проверяет валидацию типов данных.
        """
        # Arrange
        item_data = {
            "sellerID": "abc123",
            "name": "Товар",
            "price": 1000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc015_create_item_with_empty_name(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-015: Создание объявления с пустой строкой в name.
        
        Проверяет валидацию пустых значений.
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "",
            "price": 1000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc016_create_item_with_empty_json(self, api_client: APIClient):
        """
        TC-016: Создание объявления с пустым JSON.
        
        Проверяет обработку пустого тела запроса.
        """
        # Arrange
        item_data = {}
        
        # Act
        response = api_client.create_item(item_data)
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
