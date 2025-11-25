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
        """
        TC-031: Полный жизненный цикл объявления.
        
        Проверяет:
        1. Создание объявления
        2. Получение по ID
        3. Получение в списке продавца
        4. Получение статистики
        5. Консистентность данных на всех этапах
        """
        # Arrange
        item_data = {
            "sellerID": unique_seller_id,
            "name": "Интеграционный тест",
            "price": 5000,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Step 1: Создание объявления
        create_response = api_client.create_item(item_data)
        assert create_response.status_code == 200, f"Ошибка создания: {create_response.text}"
        
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Step 2: Получение по ID
        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200, f"Ошибка получения по ID: {get_response.text}"
        
        get_data = get_response.json()
        if isinstance(get_data, list):
            get_item = get_data[0] if get_data else None
        else:
            get_item = get_data
        
        assert get_item is not None, "Объявление не найдено"
        assert get_item["id"] == item_id, "ID не совпадает"
        assert get_item["name"] == item_data["name"], "name не совпадает"
        assert get_item["price"] == item_data["price"], "price не совпадает"
        
        # Step 3: Получение в списке продавца
        seller_response = api_client.get_seller_items(unique_seller_id)
        assert seller_response.status_code == 200, f"Ошибка получения списка: {seller_response.text}"
        
        seller_items = seller_response.json()
        assert isinstance(seller_items, list), "Ответ должен быть массивом"
        
        found_in_list = any(item.get("id") == item_id for item in seller_items)
        assert found_in_list, "Объявление не найдено в списке продавца"
        
        # Step 4: Получение статистики
        stat_response = api_client.get_statistic(item_id)
        assert stat_response.status_code == 200, f"Ошибка получения статистики: {stat_response.text}"
        
        stat_data = stat_response.json()
        if isinstance(stat_data, list):
            stats = stat_data[0] if stat_data else {}
        else:
            stats = stat_data
        
        # Проверяем наличие полей статистики
        assert "likes" in stats, "Поле 'likes' отсутствует в статистике"
        assert "viewCount" in stats, "Поле 'viewCount' отсутствует в статистике"
        assert "contacts" in stats, "Поле 'contacts' отсутствует в статистике"
    
    @pytest.mark.integration
    def test_tc032_multiple_items_same_seller(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-032: Создание нескольких объявлений одним продавцом.
        
        Проверяет:
        - Возможность создания множества объявлений
        - Корректное получение списка
        """
        # Arrange
        created_ids = []
        items_count = 5
        
        # Act: Создаём 5 объявлений
        for i in range(items_count):
            item_data = create_valid_item_data(
                seller_id=unique_seller_id,
                name=f"Товар #{i+1}",
                price=1000 * (i + 1)
            )
            
            response = api_client.create_item(item_data)
            assert response.status_code == 200, f"Ошибка создания объявления #{i+1}: {response.text}"
            
            created_ids.append(response.json()["id"])
        
        # Assert: Проверяем список продавца
        seller_response = api_client.get_seller_items(unique_seller_id)
        assert seller_response.status_code == 200, f"Ошибка получения списка: {seller_response.text}"
        
        seller_items = seller_response.json()
        returned_ids = {item["id"] for item in seller_items}
        
        # Проверяем, что все созданные ID присутствуют
        for created_id in created_ids:
            assert created_id in returned_ids, f"Объявление {created_id} не найдено в списке продавца"
    
    @pytest.mark.integration
    def test_tc033_item_id_uniqueness(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-033: Проверка уникальности ID объявлений.
        
        Проверяет, что два объявления с одинаковыми данными получают разные ID.
        """
        # Arrange
        identical_data = {
            "sellerID": unique_seller_id,
            "name": "Одинаковый товар",
            "price": 999,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        
        # Act: Создаём два объявления с одинаковыми данными
        response1 = api_client.create_item(identical_data)
        response2 = api_client.create_item(identical_data)
        
        # Assert
        assert response1.status_code == 200, f"Ошибка создания первого объявления: {response1.text}"
        assert response2.status_code == 200, f"Ошибка создания второго объявления: {response2.text}"
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        assert id1 != id2, f"ID объявлений должны быть уникальными, но оба равны: {id1}"
        
        # Проверяем, что оба объявления можно получить отдельно
        get_response1 = api_client.get_item(id1)
        get_response2 = api_client.get_item(id2)
        
        assert get_response1.status_code == 200, f"Не удалось получить первое объявление: {get_response1.text}"
        assert get_response2.status_code == 200, f"Не удалось получить второе объявление: {get_response2.text}"
    
    @pytest.mark.integration
    def test_tc034_seller_data_isolation(self, api_client: APIClient):
        """
        TC-034: Изоляция данных между разными продавцами.
        
        Проверяет, что объявления одного продавца не видны другому.
        """
        # Arrange
        seller_id_1 = generate_unique_seller_id()
        seller_id_2 = generate_unique_seller_id() + 1  # Гарантированно другой ID
        
        # Создаём объявление для продавца 1
        item_data_1 = create_valid_item_data(seller_id=seller_id_1, name="Товар продавца 1")
        response1 = api_client.create_item(item_data_1)
        assert response1.status_code == 200, f"Ошибка создания для продавца 1: {response1.text}"
        item_id_1 = response1.json()["id"]
        
        # Создаём объявление для продавца 2
        item_data_2 = create_valid_item_data(seller_id=seller_id_2, name="Товар продавца 2")
        response2 = api_client.create_item(item_data_2)
        assert response2.status_code == 200, f"Ошибка создания для продавца 2: {response2.text}"
        item_id_2 = response2.json()["id"]
        
        # Act: Получаем списки объявлений каждого продавца
        seller1_items_response = api_client.get_seller_items(seller_id_1)
        seller2_items_response = api_client.get_seller_items(seller_id_2)
        
        # Assert
        assert seller1_items_response.status_code == 200
        assert seller2_items_response.status_code == 200
        
        seller1_items = seller1_items_response.json()
        seller2_items = seller2_items_response.json()
        
        seller1_ids = {item["id"] for item in seller1_items}
        seller2_ids = {item["id"] for item in seller2_items}
        
        # Проверяем изоляцию
        assert item_id_1 in seller1_ids, "Объявление продавца 1 не найдено в его списке"
        assert item_id_2 in seller2_ids, "Объявление продавца 2 не найдено в его списке"
        assert item_id_1 not in seller2_ids, "Объявление продавца 1 найдено в списке продавца 2"
        assert item_id_2 not in seller1_ids, "Объявление продавца 2 найдено в списке продавца 1"
    
    @pytest.mark.integration
    def test_tc035_created_at_field(self, api_client: APIClient, unique_seller_id: int):
        """
        TC-035: Проверка поля createdAt.
        
        Проверяет:
        - Наличие поля createdAt
        - Валидный формат даты/времени
        - Время создания близко к фактическому
        """
        # Arrange
        time_before = datetime.now(timezone.utc)
        
        item_data = create_valid_item_data(seller_id=unique_seller_id)
        
        # Act
        response = api_client.create_item(item_data)
        
        time_after = datetime.now(timezone.utc)
        
        # Assert
        assert response.status_code == 200, f"Ошибка создания: {response.text}"
        
        created_item = response.json()
        
        assert "createdAt" in created_item, "Поле 'createdAt' отсутствует"
        assert created_item["createdAt"], "Поле 'createdAt' пустое"
        
        # Проверяем формат даты
        try:
            created_at = date_parser.parse(created_item["createdAt"])
        except (ValueError, TypeError) as e:
            pytest.fail(f"Невалидный формат даты в createdAt: {created_item['createdAt']}. Ошибка: {e}")
        
        # Проверяем, что время создания в пределах допустимого диапазона (± 1 минута)
        # Преобразуем в UTC для сравнения если нет timezone
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        time_diff_before = (created_at - time_before).total_seconds()
        time_diff_after = (time_after - created_at).total_seconds()
        
        # Время создания должно быть после time_before и до time_after (с погрешностью в 60 сек)
        assert time_diff_before >= -60, f"createdAt раньше времени запроса более чем на минуту"
        assert time_diff_after >= -60, f"createdAt позже времени ответа более чем на минуту"
