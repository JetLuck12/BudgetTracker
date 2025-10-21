"""
Pydantic модели для API Budget Tracker
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TransactionBase(BaseModel):
    """Базовая модель транзакции"""
    amount: float = Field(..., description="Сумма транзакции")
    category: str = Field(..., description="Категория транзакции")
    note: str = Field(..., description="Описание/комментарий")
    date: str = Field(..., description="Дата транзакции")
    type_: str = Field(..., alias="type", description="Тип транзакции (Списание/Пополнение)")
    report_id: Optional[int] = Field(None, description="ID отчёта")


class TransactionCreate(TransactionBase):
    """Модель для создания транзакции"""
    pass


class TransactionUpdate(BaseModel):
    """Модель для обновления транзакции"""
    amount: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None
    date: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")


class TransactionResponse(TransactionBase):
    """Модель ответа для транзакции"""
    id: int = Field(..., description="Уникальный ID транзакции")
    
    class Config:
        from_attributes = True


class PlanItem(BaseModel):
    """Элемент плана бюджета"""
    category: str = Field(..., description="Категория")
    plan_expense: float = Field(..., description="Запланированная сумма расходов")


class PlanCreate(BaseModel):
    """Модель для создания плана"""
    plan: List[PlanItem] = Field(..., description="Список элементов плана")


class PlanResponse(BaseModel):
    """Модель ответа для плана"""
    plan: Dict[str, float] = Field(..., description="План в виде словаря категория->сумма")


class SummaryResponse(BaseModel):
    """Модель ответа для сводки"""
    total_income: float = Field(..., description="Общий доход")
    total_expense: float = Field(..., description="Общие расходы")
    balance: float = Field(..., description="Баланс")
    categories: Dict[str, float] = Field(..., description="Сводка по категориям")


class AnalyticsResponse(BaseModel):
    """Модель ответа для аналитики"""
    expenses_by_weekday: Dict[str, float] = Field(..., description="Расходы по дням недели")
    top_categories: Dict[str, float] = Field(..., description="Топ категории расходов")
    graph_data: List[List[float]] = Field(..., description="Данные для графика")


class ImportResponse(BaseModel):
    """Модель ответа для импорта"""
    report_id: int = Field(..., description="ID созданного отчёта")
    transactions_count: int = Field(..., description="Количество импортированных транзакций")
    message: str = Field(..., description="Сообщение о результате")


class ErrorResponse(BaseModel):
    """Модель ответа для ошибок"""
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Детали ошибки")
