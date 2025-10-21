"""
Интеграционные тесты и тесты edge cases для Budget Tracker
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Добавляем путь к src для импорта модулей
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.DBManager import DBManager
from core.manager import BudgetManager
from core.transaction import Transaction
from core.summary import Summary, tran_type, EXPENSE_TYPE, INCOME_TYPE
from core.plan import Plan, PlanParser


class TestIntegration:
    """Интеграционные тесты для полного workflow"""
    
    def test_full_workflow(self, temp_db_file):
        """Тест полного workflow приложения"""
        # Создаем менеджер бюджета
        with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
            manager = BudgetManager()
        
        # Добавляем транзакции
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, -1),
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", EXPENSE_TYPE, -1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-03", EXPENSE_TYPE, -1),
            Transaction(300.0, "Продукты", "Еще продукты", "2025-01-04", EXPENSE_TYPE, -1)
        ]
        
        for transaction in transactions:
            manager.add_transaction(transaction)
        
        # Проверяем, что транзакции добавлены
        all_transactions = manager.get_transactions()
        assert len(all_transactions) == 4
        
        # Получаем финансовую сводку
        summary = manager.get_financial_summary()
        assert summary["income"] == 2000.0
        assert summary["expense"] == 1800.0
        assert summary["balance"] == 200.0
        
        # Получаем категории
        categories = manager.get_all_categories()
        assert len(categories) == 3
        assert "Зарплата" in categories
        assert "Продукты" in categories
        assert "Транспорт" in categories
        
        # Тестируем отмену операций
        manager.undo()  # Отменяем последнее добавление
        assert len(manager.get_transactions()) == 3
        
        manager.redo()  # Повторяем операцию
        assert len(manager.get_transactions()) == 4
        
        # Удаляем транзакцию
        transaction_to_delete = manager.get_transactions()[0]
        manager.delete_transaction(transaction_to_delete.id)
        assert len(manager.get_transactions()) == 3
        
        # Отменяем удаление
        manager.undo()
        assert len(manager.get_transactions()) == 4
    
    def test_plan_integration(self, temp_db_file, sample_plan_data):
        """Тест интеграции с планированием"""
        with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
            manager = BudgetManager()
        
        # Создаем план
        manager.apply_plan_state(sample_plan_data)
        
        # Проверяем, что план сохранен
        current_plan = manager.get_current_plan_state()
        assert current_plan == sample_plan_data
        
        # Добавляем транзакции и проверяем сравнение с планом
        transactions = [
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-01", EXPENSE_TYPE, -1),
            Transaction(500.0, "Транспорт", "Такси", "2025-01-02", EXPENSE_TYPE, -1)
        ]
        
        for transaction in transactions:
            manager.add_transaction(transaction)
        
        # Получаем сводку по категориям
        categories_summary = manager.get_summary_by_category()
        assert categories_summary["Продукты"] == -1000.0
        assert categories_summary["Транспорт"] == -500.0


class TestEdgeCases:
    """Тесты для edge cases и граничных условий"""
    
    def test_empty_database_operations(self, db_manager):
        """Тест операций с пустой базой данных"""
        # Получение транзакций из пустой базы
        transactions = db_manager.get_transactions()
        assert len(transactions) == 0
        
        # Получение категорий из пустой базы
        categories = db_manager.get_categories()
        assert len(categories) == 0
        
        # Получение доходов/расходов по несуществующей категории
        income = db_manager.get_income_for_category("Несуществующая категория")
        assert income == 0.0
        
        expense = db_manager.get_expense_for_category("Несуществующая категория")
        assert expense == 0.0
    
    def test_large_amounts(self, db_manager):
        """Тест работы с большими суммами"""
        large_amount = 999999999.99
        
        transaction = Transaction(
            amount=large_amount,
            category="Тест",
            note="Большая сумма",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].amount == large_amount
    
    def test_special_characters_in_data(self, db_manager):
        """Тест работы со специальными символами в данных"""
        special_data = {
            "category": "Продукты & Напитки",
            "note": "Покупка в магазине \"Супермаркет\" (скидка 10%)",
            "date": "2025-01-01"
        }
        
        transaction = Transaction(
            amount=1000.0,
            category=special_data["category"],
            note=special_data["note"],
            date=special_data["date"],
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].category == special_data["category"]
        assert transactions[0].note == special_data["note"]
    
    def test_unicode_characters(self, db_manager):
        """Тест работы с Unicode символами"""
        unicode_data = {
            "category": "Продукты 🍎",
            "note": "Покупка в магазине с эмодзи и кириллицей",
            "date": "2025-01-01"
        }
        
        transaction = Transaction(
            amount=1000.0,
            category=unicode_data["category"],
            note=unicode_data["note"],
            date=unicode_data["date"],
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].category == unicode_data["category"]
        assert transactions[0].note == unicode_data["note"]
    
    def test_zero_amount_transaction(self, db_manager):
        """Тест транзакции с нулевой суммой"""
        transaction = Transaction(
            amount=0.0,
            category="Тест",
            note="Нулевая сумма",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].amount == 0.0
    
    def test_negative_amount_transaction(self, db_manager):
        """Тест транзакции с отрицательной суммой"""
        transaction = Transaction(
            amount=-100.0,
            category="Возврат",
            note="Возврат товара",
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].amount == -100.0
    
    def test_very_long_strings(self, db_manager):
        """Тест работы с очень длинными строками"""
        long_string = "A" * 1000  # Строка длиной 1000 символов
        
        transaction = Transaction(
            amount=1000.0,
            category="Тест",
            note=long_string,
            date="2025-01-01",
            type_=EXPENSE_TYPE,
            report_id=1
        )
        
        transaction_id = db_manager.add_transaction(transaction)
        assert transaction_id is not None
        
        transactions = db_manager.get_transactions()
        assert len(transactions) == 1
        assert transactions[0].note == long_string
    
    def test_multiple_operations_undo_redo(self, budget_manager):
        """Тест множественных операций отмены/повтора"""
        # Добавляем несколько транзакций
        transactions = [
            Transaction(1000.0, "Категория1", "Транзакция1", "2025-01-01", EXPENSE_TYPE, -1),
            Transaction(2000.0, "Категория2", "Транзакция2", "2025-01-02", EXPENSE_TYPE, -1),
            Transaction(3000.0, "Категория3", "Транзакция3", "2025-01-03", EXPENSE_TYPE, -1)
        ]
        
        for transaction in transactions:
            budget_manager.add_transaction(transaction)
        
        assert len(budget_manager.get_transactions()) == 3
        
        # Отменяем все операции
        budget_manager.undo()  # Отменяем транзакцию 3
        assert len(budget_manager.get_transactions()) == 2
        
        budget_manager.undo()  # Отменяем транзакцию 2
        assert len(budget_manager.get_transactions()) == 1
        
        budget_manager.undo()  # Отменяем транзакцию 1
        assert len(budget_manager.get_transactions()) == 0
        
        # Повторяем все операции
        budget_manager.redo()  # Повторяем транзакцию 1
        assert len(budget_manager.get_transactions()) == 1
        
        budget_manager.redo()  # Повторяем транзакцию 2
        assert len(budget_manager.get_transactions()) == 2
        
        budget_manager.redo()  # Повторяем транзакцию 3
        assert len(budget_manager.get_transactions()) == 3


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_delete_nonexistent_transaction(self, budget_manager):
        """Тест удаления несуществующей транзакции"""
        with pytest.raises(ValueError, match="не найдена"):
            budget_manager.delete_transaction(999)
    
    def test_undo_when_empty_stack(self, budget_manager):
        """Тест отмены при пустом стеке"""
        result = budget_manager.undo()
        assert result is False
    
    def test_redo_when_empty_stack(self, budget_manager):
        """Тест повтора при пустом стеке"""
        result = budget_manager.redo()
        assert result is False
    
    def test_summary_with_empty_transactions(self):
        """Тест сводки с пустым списком транзакций"""
        summary = Summary.get_financial_summary([])
        assert summary["income"] == 0.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["count"] == 0
        assert summary["avg_check"] == 0.0
    
    def test_summary_with_none_transactions(self):
        """Тест сводки с None вместо списка транзакций"""
        summary = Summary.get_financial_summary(None)
        assert summary["income"] == 0.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["count"] == 0
        assert summary["avg_check"] == 0.0


class TestPerformance:
    """Тесты производительности"""
    
    @pytest.mark.slow
    def test_large_number_of_transactions(self, temp_db_file):
        """Тест работы с большим количеством транзакций"""
        with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
            manager = BudgetManager()
        
        # Добавляем 1000 транзакций
        for i in range(1000):
            transaction = Transaction(
                amount=100.0 + i,
                category=f"Категория{i % 10}",
                note=f"Транзакция {i}",
                date=f"2025-01-{(i % 28) + 1:02d}",
                type_=EXPENSE_TYPE if i % 2 == 0 else INCOME_TYPE,
                report_id=-1
            )
            manager.add_transaction(transaction)
        
        # Проверяем, что все транзакции добавлены
        transactions = manager.get_transactions()
        assert len(transactions) == 1000
        
        # Проверяем производительность получения сводки
        import time
        start_time = time.time()
        summary = manager.get_financial_summary()
        end_time = time.time()
        
        assert end_time - start_time < 1.0  # Должно выполняться менее чем за секунду
        assert summary["count"] == 1000
    
    @pytest.mark.slow
    def test_concurrent_operations(self, temp_db_file):
        """Тест конкурентных операций"""
        import threading
        import time
        
        with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
            manager = BudgetManager()
        
        results = []
        
        def add_transactions(thread_id, count):
            """Функция для добавления транзакций в отдельном потоке"""
            for i in range(count):
                transaction = Transaction(
                    amount=100.0,
                    category=f"Поток{thread_id}",
                    note=f"Транзакция {i}",
                    date="2025-01-01",
                    type_=EXPENSE_TYPE,
                    report_id=-1
                )
                manager.add_transaction(transaction)
            results.append(f"Поток {thread_id} завершен")
        
        # Создаем несколько потоков
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_transactions, args=(i, 10))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем результат
        assert len(results) == 5
        transactions = manager.get_transactions()
        assert len(transactions) == 50  # 5 потоков * 10 транзакций


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
