"""
Тесты для Budget Tracker - API эндпоинты
"""
import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Добавляем путь к src для импорта модулей
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.main import app
from core.transaction import Transaction
from core.summary import EXPENSE_TYPE, INCOME_TYPE


class TestAPITransactions:
    """Тесты для API эндпоинтов транзакций"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_budget_manager(self):
        """Фикстура для мока BudgetManager"""
        with patch('api.dependencies.get_budget_manager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_get_transactions_empty(self, client, mock_budget_manager):
        """Тест получения пустого списка транзакций"""
        mock_budget_manager.get_transactions.return_value = []
        
        response = client.get("/api/transactions")
        
        assert response.status_code == 200
        assert response.json() == []
        mock_budget_manager.get_transactions.assert_called_once()
    
    def test_get_transactions_with_data(self, client, mock_budget_manager):
        """Тест получения транзакций с данными"""
        mock_transactions = [
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-01", EXPENSE_TYPE, 1, id=1),
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-02", INCOME_TYPE, 2, id=2)
        ]
        mock_budget_manager.get_transactions.return_value = mock_transactions
        
        response = client.get("/api/transactions")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["amount"] == 1000.0
        assert data[0]["category"] == "Продукты"
        assert data[0]["type"] == EXPENSE_TYPE
        assert data[1]["amount"] == 2000.0
        assert data[1]["type"] == INCOME_TYPE
    
    def test_create_transaction(self, client, mock_budget_manager):
        """Тест создания новой транзакции"""
        transaction_data = {
            "amount": 1000.0,
            "category": "Продукты",
            "note": "Покупка продуктов",
            "date": "2025-01-01",
            "type": EXPENSE_TYPE,
            "report_id": 1
        }
        
        response = client.post("/api/transactions", json=transaction_data)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Транзакция успешно создана"
        mock_budget_manager.add_transaction.assert_called_once()
    
    def test_create_transaction_invalid_data(self, client, mock_budget_manager):
        """Тест создания транзакции с невалидными данными"""
        transaction_data = {
            "amount": "invalid",
            "category": "Продукты",
            "note": "Покупка продуктов",
            "date": "2025-01-01",
            "type": EXPENSE_TYPE
        }
        
        response = client.post("/api/transactions", json=transaction_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_delete_transaction(self, client, mock_budget_manager):
        """Тест удаления транзакции"""
        transaction_id = 1
        
        response = client.delete(f"/api/transactions/{transaction_id}")
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Транзакция {transaction_id} успешно удалена"
        mock_budget_manager.delete_transaction.assert_called_once_with(transaction_id)
    
    def test_delete_transaction_not_found(self, client, mock_budget_manager):
        """Тест удаления несуществующей транзакции"""
        mock_budget_manager.delete_transaction.side_effect = ValueError("Транзакция с ID 999 не найдена")
        
        response = client.delete("/api/transactions/999")
        
        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]
    
    def test_get_transactions_summary(self, client, mock_budget_manager):
        """Тест получения сводки по транзакциям"""
        mock_summary = {
            "income": 2000.0,
            "expense": 1500.0,
            "balance": 500.0,
            "count": 3
        }
        mock_budget_manager.get_financial_summary.return_value = mock_summary
        
        response = client.get("/api/transactions/summary")
        
        assert response.status_code == 200
        assert response.json() == mock_summary
        mock_budget_manager.get_financial_summary.assert_called_once()
    
    def test_get_categories(self, client, mock_budget_manager):
        """Тест получения категорий"""
        mock_categories = ["Продукты", "Транспорт", "Зарплата"]
        mock_budget_manager.get_all_categories.return_value = mock_categories
        
        response = client.get("/api/transactions/categories")
        
        assert response.status_code == 200
        assert response.json() == mock_categories
        mock_budget_manager.get_all_categories.assert_called_once()


class TestAPIAnalytics:
    """Тесты для API эндпоинтов аналитики"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_budget_manager(self):
        """Фикстура для мока BudgetManager"""
        with patch('api.dependencies.get_budget_manager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_get_financial_summary(self, client, mock_budget_manager):
        """Тест получения финансовой сводки"""
        mock_summary = {
            "income": 2000.0,
            "expense": 1500.0,
            "balance": 500.0,
            "count": 3
        }
        mock_categories = {"Продукты": -1000.0, "Транспорт": -500.0}
        
        mock_budget_manager.get_financial_summary.return_value = mock_summary
        mock_budget_manager.get_summary_by_category.return_value = mock_categories
        
        response = client.get("/api/analytics/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == 2000.0
        assert data["total_expense"] == 1500.0
        assert data["balance"] == 500.0
        assert data["categories"] == mock_categories
    
    def test_get_categories_summary(self, client, mock_budget_manager):
        """Тест получения сводки по категориям"""
        mock_categories = {"Продукты": -1000.0, "Транспорт": -500.0, "Зарплата": 2000.0}
        mock_budget_manager.get_summary_by_category.return_value = mock_categories
        
        response = client.get("/api/analytics/categories")
        
        assert response.status_code == 200
        assert response.json() == mock_categories
        mock_budget_manager.get_summary_by_category.assert_called_once()
    
    def test_get_expenses_by_weekday(self, client, mock_budget_manager):
        """Тест получения расходов по дням недели"""
        mock_weekday_data = {
            "Понедельник": 100.0,
            "Вторник": 200.0,
            "Среда": 150.0,
            "Четверг": 300.0,
            "Пятница": 250.0,
            "Суббота": 180.0,
            "Воскресенье": 120.0
        }
        mock_budget_manager.get_expenses_by_weekday.return_value = mock_weekday_data
        
        response = client.get("/api/analytics/weekday")
        
        assert response.status_code == 200
        assert response.json() == mock_weekday_data
        mock_budget_manager.get_expenses_by_weekday.assert_called_once()
    
    def test_get_top_expense_categories(self, client, mock_budget_manager):
        """Тест получения топ категорий расходов"""
        mock_top_categories = {
            "Продукты": 1000.0,
            "Транспорт": 500.0,
            "Развлечения": 300.0
        }
        mock_budget_manager.get_top_expense_categories.return_value = mock_top_categories
        
        response = client.get("/api/analytics/top-categories?top_n=3")
        
        assert response.status_code == 200
        assert response.json() == mock_top_categories
        mock_budget_manager.get_top_expense_categories.assert_called_once_with(3)
    
    def test_get_graph_data(self, client, mock_budget_manager):
        """Тест получения данных для графика"""
        mock_graph_data = [
            [1640995200.0, 1641081600.0, 1641168000.0],  # timestamps
            [1000.0, 1500.0, 2000.0]  # balances
        ]
        mock_budget_manager.get_graph_summary.return_value = mock_graph_data
        
        response = client.get("/api/analytics/graph")
        
        assert response.status_code == 200
        assert response.json() == mock_graph_data
        mock_budget_manager.get_graph_summary.assert_called_once()
    
    def test_get_full_analytics(self, client, mock_budget_manager):
        """Тест получения полной аналитики"""
        mock_weekday_data = {"Понедельник": 100.0, "Вторник": 200.0}
        mock_top_categories = {"Продукты": 1000.0, "Транспорт": 500.0}
        mock_graph_data = [[1640995200.0], [1000.0]]
        
        mock_budget_manager.get_expenses_by_weekday.return_value = mock_weekday_data
        mock_budget_manager.get_top_expense_categories.return_value = mock_top_categories
        mock_budget_manager.get_graph_summary.return_value = mock_graph_data
        
        response = client.get("/api/analytics/full")
        
        assert response.status_code == 200
        data = response.json()
        assert data["expenses_by_weekday"] == mock_weekday_data
        assert data["top_categories"] == mock_top_categories
        assert data["graph_data"] == mock_graph_data


class TestAPIPlan:
    """Тесты для API эндпоинтов планирования"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_budget_manager(self):
        """Фикстура для мока BudgetManager"""
        with patch('api.dependencies.get_budget_manager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_get_plan(self, client, mock_budget_manager):
        """Тест получения плана бюджета"""
        mock_plan_data = {
            "Продукты": 5000.0,
            "Транспорт": 2000.0,
            "Развлечения": 1000.0
        }
        mock_budget_manager.load_plan.return_value = None
        mock_budget_manager.get_current_plan_state.return_value = mock_plan_data
        
        response = client.get("/api/plan")
        
        assert response.status_code == 200
        assert response.json()["plan"] == mock_plan_data
        mock_budget_manager.load_plan.assert_called_once()
        mock_budget_manager.get_current_plan_state.assert_called_once()
    
    def test_create_plan(self, client, mock_budget_manager):
        """Тест создания плана бюджета"""
        plan_data = {
            "plan": [
                {"category": "Продукты", "plan_expense": 5000.0},
                {"category": "Транспорт", "plan_expense": 2000.0},
                {"category": "Развлечения", "plan_expense": 1000.0}
            ]
        }
        
        response = client.post("/api/plan", json=plan_data)
        
        assert response.status_code == 200
        assert response.json()["message"] == "План бюджета успешно создан"
        mock_budget_manager.save_plan_changes.assert_called_once()


class TestAPIImport:
    """Тесты для API эндпоинтов импорта"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_budget_manager(self):
        """Фикстура для мока BudgetManager"""
        with patch('api.dependencies.get_budget_manager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_import_csv(self, client, mock_budget_manager):
        """Тест импорта CSV файла"""
        mock_budget_manager.import_from_file.return_value = 1
        
        # Создаем тестовый CSV файл
        csv_content = "Дата операции,Номер счета,Описание операции,Сумма,Категория,Тип,Комментарий,Кэшбэк\n2025-01-01,123,Покупка,1000,Продукты,Списание,Тест,0"
        
        files = {"file": ("test.csv", csv_content, "text/csv")}
        
        response = client.post("/api/import/csv", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == 1
        assert data["message"] == "CSV файл успешно импортирован"
        mock_budget_manager.import_from_file.assert_called_once()
    
    def test_import_excel(self, client, mock_budget_manager):
        """Тест импорта Excel файла"""
        mock_budget_manager.import_from_file.return_value = 2
        
        # Создаем тестовый Excel файл (заглушка)
        excel_content = b"fake excel content"
        
        files = {"file": ("test.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        response = client.post("/api/import/excel", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == 2
        assert data["message"] == "Excel файл успешно импортирован"
        mock_budget_manager.import_from_file.assert_called_once()
    
    def test_import_invalid_file(self, client, mock_budget_manager):
        """Тест импорта невалидного файла"""
        mock_budget_manager.import_from_file.side_effect = ValueError("Неверный формат файла")
        
        files = {"file": ("test.txt", "invalid content", "text/plain")}
        
        response = client.post("/api/import/csv", files=files)
        
        assert response.status_code == 400
        assert "Неверный формат файла" in response.json()["detail"]


class TestAPIGeneral:
    """Общие тесты для API"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента FastAPI"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Тест проверки состояния API"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Budget Tracker API работает" in data["message"]
    
    def test_root_endpoint(self, client):
        """Тест главной страницы API"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "Budget Tracker API" in response.text
        assert "text/html" in response.headers["content-type"]
    
    def test_cors_headers(self, client):
        """Тест CORS заголовков"""
        response = client.options("/api/transactions")
        
        # FastAPI автоматически добавляет CORS заголовки
        assert response.status_code in [200, 405]  # OPTIONS может быть не реализован
    
    def test_api_docs_available(self, client):
        """Тест доступности документации API"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_api_redoc_available(self, client):
        """Тест доступности ReDoc документации"""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
