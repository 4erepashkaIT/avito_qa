"""
Интеграционные тесты для API объявлений.
Тест-кейсы: TC-031 — TC-035
"""
import pytest
from datetime import datetime, timezone
from dateutil import parser as date_parser
from conftest import APIClient, create_valid_item_data, generate_unique_seller_id


class TestIntegration:
    """Интеграционные тесты."""
    
    @pytest.mark.integration
    @pytest.mark.smoke
    def test_tc031_full_item_lifecycle(self, api_client: APIClient, unique_seller_id: int):
        """TC-031: Полный жизненный цикл объявления."""
        # Step 1: Создание
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Интеграционный тест",
            "price": 5000,
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
        
        create_response = api_client.create_item(item_data)
        assert create_response.status_code == 200, f"Ошибка создания: {create_response.text}"
        
        item_id = create_response.json()["id"]
        
        # Step 2: Получение по ID
        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        item = get_data[0] if isinstance(get_data, list) and get_data else get_data
        assert item["id"] == item_id
        assert item["name"] == item_data["name"]
        
        # Step 3: Получение в списке продавца
        seller_response = api_client.get_seller_items(unique_seller_id)
        assert seller_response.status_code == 200
        
        seller_items = seller_response.json()
        assert any(item.get("id") == item_id for item in seller_items)
        
        # Step 4: Получение статистики
        stat_response = api_client.get_statistic(item_id)
        assert stat_response.status_code == 200
    
    @pytest.mark.integration
    def test_tc032_multiple_items_same_seller(self, api_client: APIClient, unique_seller_id: int):
        """TC-032: Создание нескольких объявлений одним продавцом."""
        created_ids = []
        
        for i in range(5):
            item_data = {
                "sellerID": unique_seller_id,
                "name": f"Товар #{i+1}",
                "price": 1000 * (i + 1),
                "likes": 0,
                "viewCount": 0,
                "contacts": 0
            }
            
            response = api_client.create_item(item_data)
            assert response.status_code == 200, f"Ошибка создания #{i+1}: {response.text}"
            created_ids.append(response.json()["id"])
        
        # Проверяем список продавца
        seller_response = api_client.get_seller_items(unique_seller_id)
        assert seller_response.status_code == 200
        
        returned_ids = {item["id"] for item in seller_response.json()}
        for cid in created_ids:
            assert cid in returned_ids
    
    @pytest.mark.integration
    def test_tc033_item_id_uniqueness(self, api_client: APIClient, unique_seller_id: int):
        """TC-033: Проверка уникальности ID объявлений."""
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Одинаковый товар",
            "price": 999,
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
        
        response1 = api_client.create_item(item_data)
        response2 = api_client.create_item(item_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        assert id1 != id2, "ID должны быть уникальными"
    
    @pytest.mark.integration
    def test_tc034_seller_data_isolation(self, api_client: APIClient):
        """TC-034: Изоляция данных между разными продавцами."""
        seller_id_1 = generate_unique_seller_id()
        seller_id_2 = generate_unique_seller_id() + 1
        
        # Создаём объявления для разных продавцов
        item1 = {"sellerID": seller_id_1, "name": "Товар 1", "price": 100, "likes": 0, "viewCount": 0, "contacts": 0}
        item2 = {"sellerID": seller_id_2, "name": "Товар 2", "price": 200, "likes": 0, "viewCount": 0, "contacts": 0}
        
        r1 = api_client.create_item(item1)
        r2 = api_client.create_item(item2)
        
        assert r1.status_code == 200
        assert r2.status_code == 200
        
        id1 = r1.json()["id"]
        id2 = r2.json()["id"]
        
        # Проверяем изоляцию
        seller1_items = {item["id"] for item in api_client.get_seller_items(seller_id_1).json()}
        seller2_items = {item["id"] for item in api_client.get_seller_items(seller_id_2).json()}
        
        assert id1 in seller1_items
        assert id2 in seller2_items
        assert id1 not in seller2_items
        assert id2 not in seller1_items
    
    @pytest.mark.integration
    def test_tc035_created_at_field(self, api_client: APIClient, unique_seller_id: int):
        """TC-035: Проверка поля createdAt."""
        time_before = datetime.now(timezone.utc)
        
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Тест даты",
            "price": 1000,
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
        
        response = api_client.create_item(item_data)
        
        time_after = datetime.now(timezone.utc)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "createdAt" in data and data["createdAt"]
        
        # Проверяем валидность даты
        try:
            created_at = date_parser.parse(data["createdAt"])
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
        except Exception as e:
            pytest.fail(f"Невалидный формат даты: {e}")
