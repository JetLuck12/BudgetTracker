"""
Роутер для импорта данных
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ..models import ImportResponse
from ..dependencies import get_budget_manager
from src.core.manager import BudgetManager

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/csv", response_model=ImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Импорт транзакций из CSV файла"""
    try:
        # Проверяем тип файла
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
        
        # Сохраняем временный файл
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Импортируем данные
        report_id = manager.import_from_file(temp_file_path)
        
        # Удаляем временный файл
        os.remove(temp_file_path)
        
        # Получаем количество импортированных транзакций
        transactions = manager.get_transactions()
        imported_count = len([t for t in transactions if t.report_id == report_id])
        
        return ImportResponse(
            report_id=report_id,
            transactions_count=imported_count,
            message=f"Успешно импортировано {imported_count} транзакций"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {str(e)}")


@router.post("/excel", response_model=ImportResponse)
async def import_excel(
    file: UploadFile = File(...),
    manager: BudgetManager = Depends(get_budget_manager)
):
    """Импорт транзакций из Excel файла"""
    try:
        # Проверяем тип файла
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            raise HTTPException(status_code=400, detail="Файл должен быть в формате Excel (.xlsx или .xls)")
        
        # Сохраняем временный файл
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Импортируем данные
        report_id = manager.import_from_file(temp_file_path)
        
        # Удаляем временный файл
        os.remove(temp_file_path)
        
        # Получаем количество импортированных транзакций
        transactions = manager.get_transactions()
        imported_count = len([t for t in transactions if t.report_id == report_id])
        
        return ImportResponse(
            report_id=report_id,
            transactions_count=imported_count,
            message=f"Успешно импортировано {imported_count} транзакций"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {str(e)}")
