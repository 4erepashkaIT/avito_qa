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
        """
        TC-027: Получение статистики существующего объявления.
        
        Проверяет:
        - Код ответа 200 OK
        - Соответствие значений статистики
        """
        # Arrange
        expected_stats = {
            "likes": 5,
            "viewCount": 10,
            "contacts": 2
        }
        
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Товар со статистикой",
            "price": 1500,
            "statistics": expected_stats
        }
        
        # Создаём объявление
        create_response = api_client.create_item(item_data)
        assert create_response.status_code == 200, f"Не удалось создать объявление: {create_response.text}"
        
        item_id = create_response.json()["id"]
        
        # Act
        response = api_client.get_statistic(item_id)
        
        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        # Ответ может быть массивом или объектом
        if isinstance(data, list):
            assert len(data) >= 1, "Ответ не содержит статистику"
            stats = data[0]
        else:
            stats = data
        
        # Проверяем значения статистики
        assert stats.get("likes") == expected_stats["likes"], \
            f"likes не совпадает: ожидалось {expected_stats['likes']}, получено {stats.get('likes')}"
        assert stats.get("viewCount") == expected_stats["viewCount"], \
            f"viewCount не совпадает: ожидалось {expected_stats['viewCount']}, получено {stats.get('viewCount')}"
        assert stats.get("contacts") == expected_stats["contacts"], \
            f"contacts не совпадает: ожидалось {expected_stats['contacts']}, получено {stats.get('contacts')}"


class TestGetStatisticNegative:
    """Негативные тесты получения статистики объявления."""
    
    @pytest.mark.negative
    def test_tc028_get_statistic_nonexistent_item(self, api_client: APIClient):
        """
        TC-028: Получение статистики несуществующего объявления.
        
        Проверяет обработку несуществующего ресурса.
        """
        # Arrange
        nonexistent_id = "nonexistent-id-99999"
        
        # Act
        response = api_client.get_statistic(nonexistent_id)
        
        # Assert
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc029_get_statistic_with_invalid_id(self, api_client: APIClient):
        """
        TC-029: Получение статистики с невалидным ID.
        
        Проверяет обработку невалидных символов в ID.
        """
        # Arrange
        invalid_id = "!@#$%^&*()"
        
        # Act
        response = api_client.get_statistic(invalid_id)
        
        # Assert
        # Ожидается 400 или 404
        assert response.status_code in [400, 404], f"Ожидался статус 400 или 404, получен {response.status_code}"
    
    @pytest.mark.negative
    def test_tc030_get_statistic_with_empty_id(self, api_client: APIClient):
        """
        TC-030: Получение статистики с пустым ID.
        
        Проверяет обработку пустого параметра.
        """
        # Arrange
        empty_id = ""
        
        # Act
        response = api_client.get_statistic(empty_id)
        
        # Assert
        # Пустой ID может вернуть 400, 404 или перенаправить
        assert response.status_code in [400, 404, 405], f"Ожидался статус 400, 404 или 405, получен {response.status_code}"
