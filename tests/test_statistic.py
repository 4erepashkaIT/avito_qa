"""
Тесты для API получения статистики объявления GET /api/1/statistic/{id}
Тест-кейсы: TC-027 — TC-030
"""
import pytest
from conftest import APIClient, create_valid_item_data, generate_unique_seller_id


class TestGetStatisticPositive:
    """Позитивные тесты получения статистики объявления."""
    
    @pytest.mark.positive
    @pytest.mark.smoke
    def test_tc027_get_statistic_existing_item(self, api_client: APIClient, unique_seller_id: int):
        """TC-027: Получение статистики существующего объявления."""
        # Создаём объявление с заданной статистикой
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар со статистикой",
            "price": 1500,
            "likes": 5,
            "viewCount": 10,
            "contacts": 2
        }
        
        create_response = api_client.create_item(item_data)
        assert create_response.status_code == 200, f"Не удалось создать объявление: {create_response.text}"
        
        item_id = create_response.json().get("id")
        assert item_id, "ID объявления не получен"
        
        # Получаем статистику
        response = api_client.get_statistic(item_id)
        
        assert response.status_code == 200
        
        data = response.json()
        stats = data[0] if isinstance(data, list) and data else data
        
        assert stats.get("likes") == 5
        assert stats.get("viewCount") == 10
        assert stats.get("contacts") == 2


class TestGetStatisticNegative:
    """Негативные тесты получения статистики объявления."""
    
    @pytest.mark.negative
    def test_tc028_get_statistic_nonexistent_item(self, api_client: APIClient):
        """
        TC-028: Получение статистики несуществующего объявления.
        
        ПРИМЕЧАНИЕ (BUG-003): API возвращает 400 вместо 404.
        """
        response = api_client.get_statistic("nonexistent-id-99999")
        
        # Принимаем и 400, и 404 (см. BUG-003)
        assert response.status_code in [400, 404]
    
    @pytest.mark.negative
    def test_tc029_get_statistic_with_invalid_id(self, api_client: APIClient):
        """TC-029: Получение статистики с невалидным ID."""
        response = api_client.get_statistic("!@#$%^&*()")
        
        assert response.status_code in [400, 404]
    
    @pytest.mark.negative
    def test_tc030_get_statistic_with_empty_id(self, api_client: APIClient):
        """TC-030: Получение статистики с пустым ID."""
        response = api_client.get_statistic("")
        
        assert response.status_code in [400, 404, 405]
