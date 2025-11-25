"""
Тесты для API получения объявления по ID GET /api/1/item/{id}
Тест-кейсы: TC-017 — TC-021
"""
import pytest
from conftest import APIClient, create_valid_item_data


class TestGetItemPositive:
    """Позитивные тесты получения объявления по ID."""
    
    @pytest.mark.positive
    @pytest.mark.smoke
    def test_tc017_get_existing_item_by_id(self, api_client: APIClient, created_item: dict):
        """
        TC-017: Получение существующего объявления по валидному ID.
        
        Проверяет:
        - Код ответа 200 OK
        - Соответствие данных созданному объявлению
        """
        # Arrange
        item_id = created_item["id"]
        request_data = created_item["_request_data"]
        
        # Act
        response = api_client.get_item(item_id)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        # Ответ может быть массивом или объектом
        if isinstance(data, list):
            assert len(data) >= 1, "Ответ не содержит объявление"
            item = data[0]
        else:
            item = data
        
        # Проверка данных
        assert item["id"] == item_id, f"ID не совпадает: ожидался {item_id}, получен {item['id']}"
        assert item["sellerId"] == request_data["sellerID"], "sellerId не совпадает"
        assert item["name"] == request_data["name"], "name не совпадает"
        assert item["price"] == request_data["price"], "price не совпадает"
        assert "statistics" in item, "Поле 'statistics' отсутствует"
        assert "createdAt" in item, "Поле 'createdAt' отсутствует"


class TestGetItemNegative:
    """Негативные тесты получения объявления по ID."""
    
    @pytest.mark.negative
    def test_tc018_get_nonexistent_item(self, api_client: APIClient):
        """
        TC-018: Получение объявления по несуществующему ID.
        
        Проверяет обработку несуществующего ресурса.
        """
        # Arrange
        nonexistent_id = "nonexistent-id-12345"
        
        # Act
        response = api_client.get_item(nonexistent_id)
        
        # Assert
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc019_get_item_with_special_characters_id(self, api_client: APIClient):
        """
        TC-019: Получение объявления с невалидным форматом ID (специальные символы).
        
        Проверяет:
        - Обработку невалидных символов в ID
        - Отсутствие XSS уязвимости
        """
        # Arrange
        xss_id = "<script>alert('xss')</script>"
        
        # Act
        response = api_client.get_item(xss_id)
        
        # Assert
        # Ожидается 400 или 404
        assert response.status_code in [400, 404], f"Ожидался статус 400 или 404, получен {response.status_code}"
        
        # Проверка на отсутствие отражения XSS в ответе
        response_text = response.text
        assert "<script>" not in response_text.lower(), "Обнаружена потенциальная XSS уязвимость"
    
    @pytest.mark.negative
    def test_tc020_get_item_with_empty_id(self, api_client: APIClient):
        """
        TC-020: Получение объявления с пустым ID.
        
        Проверяет обработку пустого параметра.
        """
        # Arrange
        empty_id = ""
        
        # Act
        response = api_client.get_item(empty_id)
        
        # Assert
        # Пустой ID может вернуть 400, 404 или даже перенаправить на другой endpoint
        assert response.status_code in [400, 404, 405], f"Ожидался статус 400, 404 или 405, получен {response.status_code}"
    
    @pytest.mark.negative
    @pytest.mark.boundary
    def test_tc021_get_item_with_very_long_id(self, api_client: APIClient):
        """
        TC-021: Получение объявления с очень длинным ID.
        
        Проверяет:
        - Обработку граничных значений длины ID
        - Стабильность сервера
        """
        # Arrange
        long_id = "a" * 10000
        
        # Act
        response = api_client.get_item(long_id)
        
        # Assert
        # Сервер должен корректно обработать запрос без падения
        assert response.status_code in [400, 404, 414], f"Ожидался статус 400, 404 или 414, получен {response.status_code}"
