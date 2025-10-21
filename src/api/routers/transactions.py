"""
Роутер для работы с транзакциями
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ..models import TransactionCreate, TransactionResponse, TransactionUpdate
from ..dependencies import get_budget_manager
from src.core.manager import BudgetManager
from src.core.transaction import Transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить все транзакции"""
    try:
        transactions = manager.get_transactions()
        return [
            TransactionResponse(
                id=t.id,
                amount=t.amount,
                category=t.category,
                note=t.note,
                date=t.date,
                type=t.type_,  # Используем alias 'type' вместо 'type_'
                report_id=t.report_id
            ) for t in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения транзакций: {str(e)}")


@router.post("/", response_model=dict)
async def create_transaction(
    transaction: TransactionCreate,
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Создать новую транзакцию"""
    try:
        new_transaction = Transaction(
            amount=transaction.amount,
            category=transaction.category,
            note=transaction.note,
            date=transaction.date,
            type_=transaction.type_,
            report_id=transaction.report_id
        )
        manager.add_transaction(new_transaction)
        return {"message": "Транзакция успешно создана"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка создания транзакции: {str(e)}")


@router.delete("/{transaction_id}", response_model=dict)
async def delete_transaction(
    transaction_id: int,
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Удалить транзакцию по ID"""
    try:
        manager.delete_transaction(transaction_id)
        return {"message": f"Транзакция {transaction_id} успешно удалена"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления транзакции: {str(e)}")


@router.get("/summary", response_model=dict)
async def get_transactions_summary(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить сводку по транзакциям"""
    try:
        summary = manager.get_financial_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сводки: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_categories(manager: BudgetManager = Depends(get_budget_manager)):
    """Получить все категории"""
    try:
        categories = manager.get_all_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения категорий: {str(e)}")
