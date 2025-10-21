"""
Роутер для аналитики и статистики
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ..models import AnalyticsResponse, SummaryResponse
from ..dependencies import get_budget_manager
from src.core.manager import BudgetManager

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=SummaryResponse)
async def get_financial_summary(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить общую финансовую сводку"""
    try:
        summary = manager.get_financial_summary()
        # Преобразуем данные в формат, ожидаемый SummaryResponse
        return SummaryResponse(
            total_income=summary.get("income", 0.0),
            total_expense=summary.get("expense", 0.0),
            balance=summary.get("balance", 0.0),
            categories=manager.get_summary_by_category()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сводки: {str(e)}")


@router.get("/categories", response_model=Dict[str, float])
async def get_categories_summary(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить сводку по категориям"""
    try:
        from src.core.summary import tran_type
        categories = manager.get_summary_by_category(tran_type.All)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сводки по категориям: {str(e)}")


@router.get("/weekday", response_model=Dict[str, float])
async def get_expenses_by_weekday(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить средние расходы по дням недели"""
    try:
        weekday_expenses = manager.get_expenses_by_weekday()
        return weekday_expenses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики по дням недели: {str(e)}")


@router.get("/top-categories", response_model=Dict[str, float])
async def get_top_expense_categories(
    top_n: int = 5,
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Получить топ категории расходов"""
    try:
        top_categories = manager.get_top_expense_categories(top_n)
        return top_categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения топ категорий: {str(e)}")


@router.get("/graph", response_model=List[List[float]])
async def get_graph_data(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить данные для графика баланса"""
    try:
        graph_data = manager.get_graph_summary()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных графика: {str(e)}")


@router.get("/full", response_model=AnalyticsResponse)
async def get_full_analytics(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить полную аналитику"""
    try:
        expenses_by_weekday = manager.get_expenses_by_weekday()
        top_categories = manager.get_top_expense_categories(5)
        graph_data = manager.get_graph_summary()
        
        return AnalyticsResponse(
            expenses_by_weekday=expenses_by_weekday,
            top_categories=top_categories,
            graph_data=graph_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения аналитики: {str(e)}")
