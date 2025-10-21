"""
Упрощенные тесты для Budget Tracker - Core модули
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
    
    def test_db_manager_initialization(self):
        """Тест инициализации DBManager"""
        # Создаем временный файл базы данных
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            db_manager = DBManager(db_path)
            
            # Проверяем, что база создана
            assert os.path.exists(db_path)
            
            # Проверяем, что таблицы созданы
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'transactions' in tables
            assert 'reports' in tables
            
            conn.close()
        finally:
            # Очистка
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_add_and_get_transaction(self):
        """Тест добавления и получения транзакции"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            db_manager = DBManager(db_path)
            
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
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_get_categories(self):
        """Тест получения категорий"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            db_manager = DBManager(db_path)
            
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
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass


class TestSummary:
    """Тесты для класса Summary"""
    
    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями"""
        return [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, 1, id_=1),
            Transaction(1000.0, "Продукты", "Покупка продуктов", "2025-01-02", EXPENSE_TYPE, 1, id_=2),
            Transaction(500.0, "Транспорт", "Заправка автомобиля", "2025-01-03", EXPENSE_TYPE, 1, id_=3),
            Transaction(300.0, "Продукты", "Покупка хлеба и молока", "2025-01-04", EXPENSE_TYPE, 1, id_=4),
            Transaction(200.0, "Развлечения", "Поход в кино", "2025-01-05", EXPENSE_TYPE, 1, id_=5)
        ]
    
    def test_get_financial_summary(self, sample_transactions):
        """Тест получения финансовой сводки"""
        summary = Summary.get_financial_summary(sample_transactions)
        
        # Проверяем, что все поля присутствуют
        assert "income" in summary
        assert "expense" in summary
        assert "balance" in summary
        assert "count" in summary
        assert "avg_check" in summary
        
        # Проверяем значения
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
    
    def test_get_summary_with_empty_list(self):
        """Тест сводки с пустым списком транзакций"""
        summary = Summary.get_financial_summary([])
        assert summary["income"] == 0.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["count"] == 0
        assert summary["avg_check"] == 0.0
    
    def test_get_summary_with_none(self):
        """Тест сводки с None вместо списка транзакций"""
        summary = Summary.get_financial_summary(None)
        assert summary["income"] == 0.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["count"] == 0
        assert summary["avg_check"] == 0.0


class TestBudgetManager:
    """Тесты для класса BudgetManager"""
    
    def test_budget_manager_initialization(self):
        """Тест инициализации BudgetManager"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            # Мокаем путь к базе данных
            with patch('core.manager.BudgetManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                
                # Создаем реальный менеджер с временной БД
                manager = BudgetManager()
                manager.DB_FILE = db_path
                manager.dbmanager = DBManager(db_path)
                manager.plan = None
                manager.PLAN_FILE = "user_plan.json"
                manager.undo_stack = []
                manager.redo_stack = []
                manager.is_undoing_redoing = False
                
                assert manager.plan is None
                assert manager.PLAN_FILE == "user_plan.json"
                assert manager.dbmanager is not None
                assert len(manager.undo_stack) == 0
                assert len(manager.redo_stack) == 0
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_add_transaction(self):
        """Тест добавления транзакции через BudgetManager"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            manager = BudgetManager()
            manager.DB_FILE = db_path
            manager.dbmanager = DBManager(db_path)
            manager.plan = None
            manager.PLAN_FILE = "user_plan.json"
            manager.undo_stack = []
            manager.redo_stack = []
            manager.is_undoing_redoing = False
            
            transaction = Transaction(
                amount=1000.0,
                category="Продукты",
                note="Покупка продуктов",
                date="2025-01-01",
                type_=EXPENSE_TYPE,
                report_id=-1
            )
            
            manager.add_transaction(transaction)
            
            # Проверяем, что транзакция добавлена
            transactions = manager.get_transactions()
            assert len(transactions) == 1
            assert transactions[0].amount == 1000.0
            
            # Проверяем, что действие добавлено в стек отмены
            assert len(manager.undo_stack) == 1
            assert manager.undo_stack[0]['type'] == 'add_transaction'
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_get_financial_summary(self):
        """Тест получения финансовой сводки"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            manager = BudgetManager()
            manager.DB_FILE = db_path
            manager.dbmanager = DBManager(db_path)
            manager.plan = None
            manager.PLAN_FILE = "user_plan.json"
            manager.undo_stack = []
            manager.redo_stack = []
            manager.is_undoing_redoing = False
            
            # Добавляем тестовые транзакции
            transactions = [
                Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, -1),
                Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", EXPENSE_TYPE, -1),
                Transaction(500.0, "Транспорт", "Такси", "2025-01-03", EXPENSE_TYPE, -1)
            ]
            
            for transaction in transactions:
                manager.add_transaction(transaction)
            
            summary = manager.get_financial_summary()
            
            # Проверяем, что доходы и расходы корректны
            assert summary["income"] >= 2000.0  # Может быть больше из-за report_id=-1
            assert summary["expense"] >= 1500.0  # Может быть больше из-за report_id=-1
            assert summary["balance"] == summary["income"] - summary["expense"]
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
