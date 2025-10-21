"""
Супер простые тесты для Budget Tracker - только основные функции без фикстур
"""
import pytest
import os
import tempfile
import sqlite3
from datetime import datetime

# Добавляем путь к src для импорта модулей
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.transaction import Transaction, from_list
from core.summary import Summary, tran_type, EXPENSE_TYPE, INCOME_TYPE


class TestTransactionBasic:
    """Базовые тесты для класса Transaction"""
    
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


class TestSummaryBasic:
    """Базовые тесты для класса Summary"""
    
    def test_get_financial_summary_single_transaction(self):
        """Тест получения финансовой сводки с одной транзакцией"""
        # Создаем только одну транзакцию
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, 1)
        ]
        
        summary = Summary.get_financial_summary(transactions)
        
        # Проверяем, что все поля присутствуют
        assert "income" in summary
        assert "expense" in summary
        assert "balance" in summary
        assert "count" in summary
        assert "avg_check" in summary
        
        # Проверяем значения
        assert summary["income"] == 2000.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 2000.0
        assert summary["count"] == 1
        assert summary["avg_check"] == 2000.0
    
    def test_get_financial_summary_two_transactions(self):
        """Тест получения финансовой сводки с двумя транзакциями"""
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", 1, INCOME_TYPE),
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", 1, EXPENSE_TYPE)
        ]
        
        summary = Summary.get_financial_summary(transactions)
        
        assert summary["income"] == 2000.0
        assert summary["expense"] == 1000.0
        assert summary["balance"] == 1000.0
        assert summary["count"] == 2
        assert summary["avg_check"] == 1000.0  # 2000 / 2
    
    def test_get_summary_by_category_simple(self):
        """Тест получения сводки по категориям с простыми данными"""
        transactions = [
            Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", 1, INCOME_TYPE),
            Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", 1, EXPENSE_TYPE)
        ]
        
        # Тест для всех типов
        summary_all = Summary.get_summary_by_category(transactions, tran_type.All)
        assert summary_all["Зарплата"] == 2000.0
        assert summary_all["Продукты"] == -1000.0
        
        # Тест только для доходов
        summary_income = Summary.get_summary_by_category(transactions, tran_type.Income)
        assert summary_income["Зарплата"] == 2000.0
        assert summary_income["Продукты"] == 0.0
        
        # Тест только для расходов
        summary_expense = Summary.get_summary_by_category(transactions, tran_type.Outcome)
        assert summary_expense["Зарплата"] == 0.0
        assert summary_expense["Продукты"] == -1000.0
    
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
