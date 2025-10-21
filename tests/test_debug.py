"""
Отладочные тесты для Budget Tracker
"""
import pytest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.transaction import Transaction
from core.summary import Summary, tran_type, EXPENSE_TYPE, INCOME_TYPE


def test_debug_summary():
    """Отладочный тест для понимания проблемы"""
    print("\n=== ОТЛАДОЧНЫЙ ТЕСТ ===")
    
    # Создаем простые транзакции
    transactions = [
        Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", 1, INCOME_TYPE),
        Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", 1, EXPENSE_TYPE)
    ]
    
    print(f"Количество транзакций: {len(transactions)}")
    for i, t in enumerate(transactions):
        print(f"Транзакция {i}: {t.amount} {t.category} {t.type_}")
    
    # Тестируем финансовую сводку
    summary = Summary.get_financial_summary(transactions)
    print(f"Финансовая сводка: {summary}")
    
    # Тестируем сводку по категориям
    summary_cat = Summary.get_summary_by_category(transactions, tran_type.All)
    print(f"Сводка по категориям: {summary_cat}")
    
    # Проверяем ожидаемые значения
    expected_income = 2000.0
    expected_expense = 1000.0
    
    print(f"Ожидаемый доход: {expected_income}, фактический: {summary['income']}")
    print(f"Ожидаемый расход: {expected_expense}, фактический: {summary['expense']}")
    
    assert summary["income"] == expected_income, f"Доход: ожидалось {expected_income}, получено {summary['income']}"
    assert summary["expense"] == expected_expense, f"Расход: ожидалось {expected_expense}, получено {summary['expense']}"


def test_debug_single_transaction():
    """Отладочный тест с одной транзакцией"""
    print("\n=== ОТЛАДОЧНЫЙ ТЕСТ С ОДНОЙ ТРАНЗАКЦИЕЙ ===")
    
    transaction = Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", 1, INCOME_TYPE)
    print(f"Транзакция: {transaction.amount} {transaction.category} {transaction.type_}")
    
    summary = Summary.get_financial_summary([transaction])
    print(f"Финансовая сводка: {summary}")
    
    assert summary["income"] == 2000.0
    assert summary["expense"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
