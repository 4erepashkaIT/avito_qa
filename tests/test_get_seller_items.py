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
        """TC-022: Получение всех объявлений существующего продавца."""
        if not multiple_items:
            pytest.skip("Не удалось создать тестовые объявления")
        
        seller_id = multiple_items[0]["sellerId"]
        created_ids = {item["id"] for item in multiple_items}
        
        response = api_client.get_seller_items(seller_id)
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        returned_ids = {item["id"] for item in data}
        assert created_ids.issubset(returned_ids), "Не все созданные объявления найдены"
    
    @pytest.mark.positive
    def test_tc023_get_seller_items_no_items(self, api_client: APIClient):
        """TC-023: Получение объявлений продавца без объявлений."""
        # Уникальный seller_id, у которого точно нет объявлений
        unique_id = generate_unique_seller_id() + 999999
        
        response = api_client.get_seller_items(unique_id)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetSellerItemsNegative:
    """Негативные тесты получения объявлений продавца."""
    
    @pytest.mark.negative
    def test_tc024_get_seller_items_with_string_id(self, api_client: APIClient):
        """TC-024: Получение объявлений с невалидным sellerID (строка)."""
        response = api_client.session.get(f"{api_client.base_url}/api/1/abc/item")
        
        assert response.status_code == 400
    
    @pytest.mark.negative
    def test_tc025_get_seller_items_with_negative_id(self, api_client: APIClient):
        """TC-025: Получение объявлений с отрицательным sellerID."""
        response = api_client.get_seller_items(-123)
        
        # Допускается 400 или 200 с пустым массивом
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert isinstance(response.json(), list)
    
    @pytest.mark.negative
    @pytest.mark.boundary
    def test_tc026_get_seller_items_with_zero_id(self, api_client: APIClient):
        """TC-026: Получение объявлений с sellerID = 0."""
        response = api_client.get_seller_items(0)
        
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert isinstance(response.json(), list)
