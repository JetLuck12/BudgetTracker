"""
Роутер для работы с планами бюджета
"""
from fastapi import APIRouter, Depends, HTTPException
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ..models import PlanCreate, PlanResponse
from ..dependencies import get_budget_manager
from src.core.manager import BudgetManager

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.get("/", response_model=PlanResponse)
async def get_plan(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить текущий план бюджета"""
    try:
        manager.load_plan()
        if not manager.plan:
            return PlanResponse(plan={})
        
        return PlanResponse(plan=manager.get_current_plan_state())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения плана: {str(e)}")


@router.post("/", response_model=dict)
async def create_plan(
    plan_data: PlanCreate,
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Создать новый план бюджета"""
    try:
        from src.core.plan import Plan
        
        # Преобразуем данные в формат Plan
        plan_dict = {item.category: item.plan_expense for item in plan_data.plan}
        
        # Создаем план
        plan = Plan([{"category": cat, "plan_expense": amount} for cat, amount in plan_dict.items()])
        
        # Сохраняем план
        manager.save_plan(plan)
        manager.plan = plan
        
        return {"message": "План успешно создан"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка создания плана: {str(e)}")


@router.put("/", response_model=dict)
async def update_plan(
    plan_data: PlanCreate,
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Обновить существующий план бюджета"""
    try:
        from src.core.plan import Plan
        
        # Получаем текущее состояние плана
        old_state = manager.get_current_plan_state()
        
        # Преобразуем данные в формат Plan
        plan_dict = {item.category: item.plan_expense for item in plan_data.plan}
        
        # Создаем новый план
        plan = Plan([{"category": cat, "plan_expense": amount} for cat, amount in plan_dict.items()])
        
        # Сохраняем изменения в стек отмены
        manager.save_plan_changes(old_state, plan_dict)
        
        # Сохраняем план
        manager.save_plan(plan)
        manager.plan = plan
        
        return {"message": "План успешно обновлён"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обновления плана: {str(e)}")


@router.get("/progress", response_model=dict)
async def get_plan_progress(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить прогресс выполнения плана"""
    try:
        manager.load_plan()
        if not manager.plan:
            return {"message": "План не найден"}
        
        plan_state = manager.get_current_plan_state()
        expenses_by_category = manager.get_summary_by_category()
        
        progress = {}
        for category, planned_amount in plan_state.items():
            actual_amount = expenses_by_category.get(category, 0)
            progress[category] = {
                "planned": planned_amount,
                "actual": actual_amount,
                "remaining": planned_amount - actual_amount,
                "percentage": (actual_amount / planned_amount * 100) if planned_amount > 0 else 0
            }
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения прогресса: {str(e)}")
