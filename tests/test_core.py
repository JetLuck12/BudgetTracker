"""
Тесты для Budget Tracker - Core модули
"""
import pytest
import os
import tempfile
import sqlite3
from datetime import datetime
from unittest.mock import patch, MagicMock

# Добавляем путь к src для импорта модулей
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.DBManager import DBManager
from core.transaction import Transaction, from_list
from core.summary import Summary, tran_type, EXPENSE_TYPE, INCOME_TYPE
from core.manager import BudgetManager


class TestTransaction:
    """Тесты для класса Transaction"""
    
    def test_transaction_creation(self):
        """Тест создания транзакции"""
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        assert transaction.amount == 1000.0
        assert transaction.category == "Продукты"
        assert transaction.note == "Покупка продуктов"
        assert transaction.date == "2025-01-01"
        assert transaction.type_ == EXPENSE_TYPE
        assert transaction.report_id == 1
    
    def test_transaction_str_representation(self):
        """Тест строкового представления транзакции"""
        transaction = Transaction(
            amount=500.0,
            category="Транспорт",
            note="Такси",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        str_repr = str(transaction)
        assert "1" in str_repr  # report_id
        assert "-" in str_repr  # знак для расхода
        assert "500.0" in str_repr  # сумма
        assert "Транспорт" in str_repr  # категория
    
    def test_from_list_function(self):
        """Тест функции from_list для создания списка транзакций"""
        raw_transactions = [
            (1, "2025-01-01", 1000.0, "Продукты", "Покупка", 1, EXPENSE_TYPE),
            (2, "2025-01-02", 500.0, "Транспорт", "Такси", 1, EXPENSE_TYPE),
            (3, "2025-01-03", 2000.0, "Зарплата", "Зарплата", 2, INCOME_TYPE)
        ]
        
        transactions = from_list(raw_transactions)
        
        assert len(transactions) == 3
        assert transactions[0].amount == 1000.0
        assert transactions[1].category == "Транспорт"
        assert transactions[2].type_ == INCOME_TYPE


class TestDBManager:
    """Тесты для класса DBManager"""
    
    @pytest.fixture
    def temp_db(self):
        """Фикстура для временной базы данных"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        yield db_path
        
        # Очистка после теста
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_db_manager_initialization(self, temp_db):
        """Тест инициализации DBManager"""
        db_manager = DBManager(temp_db)
        
        # Проверяем, что база создана
        assert os.path.exists(temp_db)
        
        # Проверяем, что таблицы созданы
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'transactions' in tables
        assert 'reports' in tables
        
        conn.close()
    
    def test_add_transaction(self, temp_db):
        """Тест добавления транзакции"""
        db_manager = DBManager(temp_db)
        
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        
        assert transaction_id is not None
        assert transaction_id > 0
        
        # Проверяем, что транзакция добавлена в базу
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].amount == 1000.0
        assert transactions[0].category == "Продукты"
    
    def test_get_categories(self, temp_db):
        """Тест получения категорий"""
        db_manager = DBManager(temp_db)
        
        # Добавляем несколько транзакций с разными категориями
        transactions = [
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-01", EXPENSE_TYPE, 1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-02", EXPENSE_TYPE, 1),
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-03", INCOME_TYPE, 2),
            Transaction(300.0, "Продукты", "Еще продукты", "2025-01-04", EXPENSE_TYPE, 1)
        ]
        
        for transaction in transactions:
            db_manager.add_transaction(transaction)
        
        categories = db_manager.get_categories()
        
        assert len(categories) == 3
        assert "Продукты" in categories
        assert "Транспорт" in categories
        assert "Зарплата" in categories
    
    def test_delete_transaction(self, temp_db):
        """Тест удаления транзакции"""
        db_manager = DBManager(temp_db)
        
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        
        # Проверяем, что транзакция добавлена
        assert len(db_manager.get_transactions()) == 1
        
        # Удаляем транзакцию
        db_manager.delete_transaction(transaction_id)
        
        # Проверяем, что транзакция удалена
        assert len(db_manager.get_transactions()) == 0
    
    def test_get_income_for_category(self, temp_db):
        """Тест получения доходов по категории"""
        db_manager = DBManager(temp_db)
        
        # Добавляем транзакции
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, 1),
            Transaction(500.0, "Зарплата", "Премия", "2025-01-02", INCOME_TYPE, 1),
            Transaction(1000.0, "Зарплата", "Расход", "2025-01-03", EXPENSE_TYPE, 1)
        ]
        
        for transaction in transactions:
            db_manager.add_transaction(transaction)
        
        income = db_manager.get_income_for_category("Зарплата")
        
        assert income == 2500.0  # 2000 + 500
    
    def test_get_expense_for_category(self, temp_db):
        """Тест получения расходов по категории"""
        db_manager = DBManager(temp_db)
        
        # Добавляем транзакции
        transactions = [
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-01", EXPENSE_TYPE, 1),
            Transaction(500.0, "Продукты", "Еще покупка", "2025-01-02", EXPENSE_TYPE, 1),
            Transaction(2000.0, "Продукты", "Доход", "2025-01-03", INCOME_TYPE, 1)
        ]
        
        for transaction in transactions:
            db_manager.add_transaction(transaction)
        
        expense = db_manager.get_expense_for_category("Продукты")
        
        assert expense == 1500.0  # 1000 + 500


class TestSummary:
    """Тесты для класса Summary"""
    
    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями"""
        return [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, 1),
            Transaction(1000.0, "Продукты", "Покупка продуктов", "2025-01-02", EXPENSE_TYPE, 1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-03", EXPENSE_TYPE, 1),
            Transaction(300.0, "Продукты", "Еще продукты", "2025-01-04", EXPENSE_TYPE, 1),
            Transaction(200.0, "Развлечения", "Кино", "2025-01-05", EXPENSE_TYPE, 1)
        ]
    
    def test_get_financial_summary(self, sample_transactions):
        """Тест получения финансовой сводки"""
        summary = Summary.get_financial_summary(sample_transactions)
        
        assert summary["income"] == 2000.0
        assert summary["expense"] == 2000.0  # 1000 + 500 + 300 + 200
        assert summary["balance"] == 0.0
        assert summary["count"] == 5
        assert summary["avg_check"] == 400.0  # 2000 / 5
    
    def test_get_summary_by_category_all(self, sample_transactions):
        """Тест получения сводки по категориям (все типы)"""
        summary = Summary.get_summary_by_category(sample_transactions, tran_type.All)
        
        assert summary["Зарплата"] == 2000.0
        assert summary["Продукты"] == -1300.0  # -1000 - 300
        assert summary["Транспорт"] == -500.0
        assert summary["Развлечения"] == -200.0
    
    def test_get_summary_by_category_income_only(self, sample_transactions):
        """Тест получения сводки по категориям (только доходы)"""
        summary = Summary.get_summary_by_category(sample_transactions, tran_type.Income)
        
        assert summary["Зарплата"] == 2000.0
        assert summary["Продукты"] == 0.0
        assert summary["Транспорт"] == 0.0
        assert summary["Развлечения"] == 0.0
    
    def test_get_summary_by_category_expense_only(self, sample_transactions):
        """Тест получения сводки по категориям (только расходы)"""
        summary = Summary.get_summary_by_category(sample_transactions, tran_type.Outcome)
        
        assert summary["Зарплата"] == 0.0
        assert summary["Продукты"] == -1300.0
        assert summary["Транспорт"] == -500.0
        assert summary["Развлечения"] == -200.0
    
    def test_get_summary_by_weekday(self, sample_transactions):
        """Тест получения сводки по дням недели"""
        # Мокаем pandas для тестирования
        with patch('core.summary.pd') as mock_pd:
            mock_df = MagicMock()
            mock_pd.DataFrame.return_value = mock_df
            
            # Настраиваем мок для фильтрации расходов
            mock_df.__getitem__.return_value = mock_df
            mock_df.empty = False
            
            # Настраиваем мок для группировки
            mock_groupby = MagicMock()
            mock_df.groupby.return_value = mock_groupby
            mock_groupby.__getitem__.return_value = mock_groupby
            mock_groupby.mean.return_value = mock_groupby
            mock_groupby.reindex.return_value = mock_groupby
            mock_groupby.to_dict.return_value = {"Понедельник": 100.0}
            
            result = Summary.get_summary_by_weekday(sample_transactions)
            
            assert isinstance(result, dict)
            mock_pd.DataFrame.assert_called_once()
    
    def test_get_top_expenses(self, sample_transactions):
        """Тест получения топ расходов"""
        # Мокаем pandas для тестирования
        with patch('core.summary.pd') as mock_pd:
            mock_df = MagicMock()
            mock_pd.DataFrame.return_value = mock_df
            
            # Настраиваем мок для фильтрации расходов
            mock_df.__getitem__.return_value = mock_df
            mock_df.empty = False
            
            # Настраиваем мок для группировки и сортировки
            mock_groupby = MagicMock()
            mock_df.groupby.return_value = mock_groupby
            mock_groupby.__getitem__.return_value = mock_groupby
            mock_groupby.sum.return_value = mock_groupby
            mock_groupby.sort_values.return_value = mock_groupby
            mock_groupby.head.return_value = mock_groupby
            mock_groupby.to_dict.return_value = {"Продукты": 1300.0, "Транспорт": 500.0}
            
            result = Summary.get_top_expenses(sample_transactions, top_n=2)
            
            assert isinstance(result, dict)
            mock_pd.DataFrame.assert_called_once()
    
    def test_get_graph_summary(self, sample_transactions):
        """Тест получения данных для графика"""
        # Мокаем pandas для тестирования
        with patch('core.summary.pd') as mock_pd:
            mock_df = MagicMock()
            mock_pd.DataFrame.return_value = mock_df
            
            # Настраиваем мок для обработки данных
            mock_df.sort_values.return_value = mock_df
            mock_df.apply.return_value = mock_df
            mock_df.groupby.return_value = mock_df
            mock_df.sum.return_value = mock_df
            mock_df.cumsum.return_value = mock_df
            
            # Настраиваем мок для индекса и значений
            mock_df.index = [datetime(2025, 1, 1), datetime(2025, 1, 2)]
            mock_df.values = [1000.0, 1500.0]
            
            result = Summary.get_graph_summary(sample_transactions)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert isinstance(result[0], list)
            assert isinstance(result[1], list)
            mock_pd.DataFrame.assert_called_once()


class TestBudgetManager:
    """Тесты для класса BudgetManager"""
    
    @pytest.fixture
    def temp_db(self):
        """Фикстура для временной базы данных"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        yield db_path
        
        # Очистка после теста
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def budget_manager(self, temp_db):
        """Фикстура для BudgetManager с временной БД"""
        with patch.object(BudgetManager, '__init__', lambda self: setattr(self, 'DB_FILE', temp_db) or setattr(self, 'dbmanager', DBManager(temp_db)) or setattr(self, 'plan', None) or setattr(self, 'PLAN_FILE', "user_plan.json") or setattr(self, 'undo_stack', []) or setattr(self, 'redo_stack', []) or setattr(self, 'is_undoing_redoing', False)):
            manager = BudgetManager()
            return manager
    
    def test_budget_manager_initialization(self, budget_manager):
        """Тест инициализации BudgetManager"""
        assert budget_manager.plan is None
        assert budget_manager.PLAN_FILE == "user_plan.json"
        assert budget_manager.dbmanager is not None
        assert len(budget_manager.undo_stack) == 0
        assert len(budget_manager.redo_stack) == 0
    
    def test_add_transaction(self, budget_manager):
        """Тест добавления транзакции через BudgetManager"""
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=-1
        )
        
        budget_manager.add_transaction(transaction)
        
        # Проверяем, что транзакция добавлена
        transactions = budget_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].amount == 1000.0
        
        # Проверяем, что действие добавлено в стек отмены
        assert len(budget_manager.undo_stack) == 1
        assert budget_manager.undo_stack[0]['type'] == 'add_transaction'
    
    def test_delete_transaction(self, budget_manager):
        """Тест удаления транзакции через BudgetManager"""
        # Сначала добавляем транзакцию
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=-1
        )
        
        budget_manager.add_transaction(transaction)
        transactions = budget_manager.get_transactions()
        transaction_id = transactions[0].id
        
        # Удаляем транзакцию
        budget_manager.delete_transaction(transaction_id)
        
        # Проверяем, что транзакция удалена
        transactions = budget_manager.get_transactions()
        assert len(transactions) == 0
        
        # Проверяем, что действие добавлено в стек отмены
        assert len(budget_manager.undo_stack) == 2  # add + delete
        assert budget_manager.undo_stack[0]['type'] == 'delete_transaction'
    
    def test_get_financial_summary(self, budget_manager):
        """Тест получения финансовой сводки"""
        # Добавляем тестовые транзакции
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, -1),
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", EXPENSE_TYPE, -1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-03", EXPENSE_TYPE, -1)
        ]
        
        for transaction in transactions:
            budget_manager.add_transaction(transaction)
        
        summary = budget_manager.get_financial_summary()
        
        assert summary["income"] == 2000.0
        assert summary["expense"] == 1500.0
        assert summary["balance"] == 500.0
    
    def test_undo_operation(self, budget_manager):
        """Тест операции отмены"""
        # Добавляем транзакцию
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=-1
        )
        
        budget_manager.add_transaction(transaction)
        
        # Проверяем, что транзакция добавлена
        assert len(budget_manager.get_transactions()) == 1
        
        # Отменяем операцию
        result = budget_manager.undo()
        
        assert result is True
        assert len(budget_manager.get_transactions()) == 0
        assert len(budget_manager.redo_stack) == 1
    
    def test_redo_operation(self, budget_manager):
        """Тест операции повтора"""
        # Добавляем транзакцию
        transaction = Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=-1
        )
        
        budget_manager.add_transaction(transaction)
        
        # Отменяем операцию
        budget_manager.undo()
        assert len(budget_manager.get_transactions()) == 0
        
        # Повторяем операцию
        result = budget_manager.redo()
        
        assert result is True
        assert len(budget_manager.get_transactions()) == 1
        assert len(budget_manager.undo_stack) == 1
    
    def test_get_all_categories(self, budget_manager):
        """Тест получения всех категорий"""
        # Добавляем транзакции с разными категориями
        transactions = [
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-01", EXPENSE_TYPE, -1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-02", EXPENSE_TYPE, -1),
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-03", INCOME_TYPE, -1)
        ]
        
        for transaction in transactions:
            budget_manager.add_transaction(transaction)
        
        categories = budget_manager.get_all_categories()
        
        assert len(categories) == 3
        assert "Продукты" in categories
        assert "Транспорт" in categories
        assert "Зарплата" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
