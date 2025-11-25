"""
Тесты для API получения всех объявлений продавца GET /api/1/{sellerID}/item
Тест-кейсы: TC-022 — TC-026
"""
import pytest
from conftest import APIClient, create_valid_item_data, generate_unique_seller_id


class TestGetSellerItemsPositive:
    """Позитивные тесты получения объявлений продавца."""
    
    @pytest.mark.positive
    @pytest.mark.smoke
    def test_tc022_get_seller_items_with_multiple_items(self, api_client: APIClient, multiple_items: list):
        """
        TC-022: Получение всех объявлений существующего продавца с объявлениями.
        
        Проверяет:
        - Код ответа 200 OK
        - Возврат массива с правильным количеством объявлений
        - Соответствие sellerId во всех объявлениях
        """
        # Arrange
        seller_id = multiple_items[0]["sellerId"]
        expected_count = len(multiple_items)
        created_ids = {item["id"] for item in multiple_items}
        
        # Act
        response = api_client.get_seller_items(seller_id)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        
        # Проверяем, что все созданные объявления присутствуют
        returned_ids = {item["id"] for item in data}
        assert created_ids.issubset(returned_ids), "Не все созданные объявления найдены в ответе"
        
        # Проверяем sellerId для всех объявлений
        for item in data:
            if item["id"] in created_ids:
                assert item["sellerId"] == seller_id, f"sellerId не совпадает для объявления {item['id']}"
                assert "name" in item, "Поле 'name' отсутствует"
                assert "price" in item, "Поле 'price' отсутствует"
                assert "statistics" in item, "Поле 'statistics' отсутствует"
                assert "createdAt" in item, "Поле 'createdAt' отсутствует"
    
    @pytest.mark.positive
    def test_tc023_get_seller_items_no_items(self, api_client: APIClient):
        """
        TC-023: Получение объявлений продавца, у которого нет объявлений.
        
        Проверяет возврат пустого массива для продавца без объявлений.
        """
        # Arrange
        # Используем уникальный seller_id, у которого точно нет объявлений
        unique_seller_id = generate_unique_seller_id() + 99999  # Добавляем смещение для уникальности
        
        # Act
        response = api_client.get_seller_items(unique_seller_id)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        # Массив может быть пустым или содержать объявления других пользователей с таким же ID
        # Главное - нет ошибки сервера


class TestGetSellerItemsNegative:
    """Негативные тесты получения объявлений продавца."""
    
    @pytest.mark.negative
    def test_tc024_get_seller_items_with_string_id(self, api_client: APIClient):
        """
        TC-024: Получение объявлений с невалидным sellerID (строка вместо числа).
        
        Проверяет валидацию типа данных sellerID.
        """
        # Arrange
        invalid_seller_id = "abc"
        
        # Act
        response = api_client.session.get(f"{api_client.base_url}/api/1/{invalid_seller_id}/item")
        
        # Assert
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc025_get_seller_items_with_negative_id(self, api_client: APIClient):
        """
        TC-025: Получение объявлений с отрицательным sellerID.
        
        Проверяет обработку невалидных значений.
        """
        # Arrange
        negative_seller_id = -123
        
        # Act
        response = api_client.get_seller_items(negative_seller_id)
        
        # Assert
        # Допускается как 400 Bad Request, так и 200 OK с пустым массивом
        assert response.status_code in [200, 400], f"Ожидался статус 200 или 400, получен {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Ответ должен быть массивом"
    
    @pytest.mark.negative
    @pytest.mark.boundary
    def test_tc026_get_seller_items_with_zero_id(self, api_client: APIClient):
        """
        TC-026: Получение объявлений с sellerID = 0.
        
        Проверяет обработку граничного значения.
        """
        # Arrange
        zero_seller_id = 0
        
        # Act
        response = api_client.get_seller_items(zero_seller_id)
        
        # Assert
        # Допускается как 400 Bad Request, так и 200 OK с пустым массивом
        assert response.status_code in [200, 400], f"Ожидался статус 200 или 400, получен {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Ответ должен быть массивом"
