"""
Зависимости для FastAPI приложения
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.core.manager import BudgetManager

# Создаем глобальный экземпляр BudgetManager для всех запросов
_budget_manager = None


def get_budget_manager() -> BudgetManager:
    """Получить экземпляр BudgetManager (singleton)"""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = BudgetManager()
    return _budget_manager
