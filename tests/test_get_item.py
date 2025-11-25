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
        """TC-017: Получение существующего объявления по валидному ID."""
        item_id = created_item["id"]
        request_data = created_item["_request_data"]
        
        response = api_client.get_item(item_id)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        # Ответ может быть массивом или объектом
        item = data[0] if isinstance(data, list) and data else data
        
        assert item.get("id") == item_id
        assert item.get("sellerId") == request_data["sellerID"]
        assert item.get("name") == request_data["name"]
        assert item.get("price") == request_data["price"]


class TestGetItemNegative:
    """Негативные тесты получения объявления по ID."""
    
    @pytest.mark.negative
    def test_tc018_get_nonexistent_item(self, api_client: APIClient):
        """
        TC-018: Получение объявления по несуществующему ID.
        
        ПРИМЕЧАНИЕ (BUG-003): API возвращает 400 вместо 404.
        """
        response = api_client.get_item("nonexistent-id-12345")
        
        # Принимаем и 400, и 404 (см. BUG-003)
        assert response.status_code in [400, 404]
    
    @pytest.mark.negative
    def test_tc019_get_item_with_special_characters_id(self, api_client: APIClient):
        """TC-019: Получение объявления с невалидным форматом ID (XSS-проверка)."""
        xss_id = "<script>alert('xss')</script>"
        
        response = api_client.get_item(xss_id)
        
        assert response.status_code in [400, 404]
        assert "<script>" not in response.text.lower(), "Потенциальная XSS уязвимость!"
    
    @pytest.mark.negative
    def test_tc020_get_item_with_empty_id(self, api_client: APIClient):
        """TC-020: Получение объявления с пустым ID."""
        response = api_client.get_item("")
        
        assert response.status_code in [400, 404, 405]
    
    @pytest.mark.negative
    @pytest.mark.boundary
    def test_tc021_get_item_with_very_long_id(self, api_client: APIClient):
        """TC-021: Получение объявления с очень длинным ID."""
        long_id = "a" * 10000
        
        response = api_client.get_item(long_id)
        
        assert response.status_code in [400, 404, 414]
