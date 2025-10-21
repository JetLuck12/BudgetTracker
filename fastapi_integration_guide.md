# Интеграция FastAPI в Budget Tracker

## Обзор

FastAPI - это современный веб-фреймворк для создания API на Python. В контексте нашего бюджетного трекера FastAPI может быть использован для создания REST API, которое позволит:

1. **Веб-интерфейс** - создать веб-версию приложения
2. **Мобильное приложение** - предоставить API для мобильного клиента
3. **Интеграции** - подключить внешние сервисы и банки
4. **Автоматизация** - создать скрипты для автоматического импорта данных

## Где можно использовать FastAPI в проекте

### 1. REST API для управления транзакциями

```python
# Примеры endpoints:
GET /api/transactions          # Получить все транзакции
POST /api/transactions         # Добавить новую транзакцию
PUT /api/transactions/{id}     # Обновить транзакцию
DELETE /api/transactions/{id}  # Удалить транзакцию
GET /api/transactions/summary  # Получить сводку по транзакциям
```

### 2. API для работы с планами бюджета

```python
# Примеры endpoints:
GET /api/plan                 # Получить текущий план
POST /api/plan                # Создать новый план
PUT /api/plan                 # Обновить план
GET /api/plan/progress        # Получить прогресс выполнения плана
```

### 3. API для аналитики и статистики

```python
# Примеры endpoints:
GET /api/analytics/summary    # Общая финансовая сводка
GET /api/analytics/categories # Статистика по категориям
GET /api/analytics/trends     # Тренды расходов
GET /api/analytics/weekday    # Статистика по дням недели
```

### 4. API для импорта данных

```python
# Примеры endpoints:
POST /api/import/csv          # Импорт из CSV файла
POST /api/import/excel        # Импорт из Excel файла
POST /api/import/bank         # Импорт из банковского API
```

## Архитектурные решения

### Вариант 1: Отдельный FastAPI сервер

```
src/
├── core/           # Существующая бизнес-логика
├── ui/            # Существующий PyQt6 интерфейс
├── api/           # Новый FastAPI сервер
│   ├── main.py    # Точка входа FastAPI
│   ├── routers/   # Маршруты API
│   ├── models/    # Pydantic модели
│   └── dependencies.py
└── main.py        # Существующая точка входа PyQt6
```

**Преимущества:**
- Независимость от существующего кода
- Возможность запуска отдельно
- Легкое тестирование

**Недостатки:**
- Дублирование логики
- Необходимость синхронизации данных

### Вариант 2: Интеграция в существующую архитектуру

```
src/
├── core/
│   ├── manager.py     # Существующий BudgetManager
│   └── api_manager.py # Новый APIManager
├── ui/               # Существующий PyQt6 интерфейс
├── api/              # FastAPI компоненты
└── main.py           # Обновленная точка входа
```

**Преимущества:**
- Переиспользование существующей логики
- Единая точка управления данными
- Меньше дублирования кода

**Недостатки:**
- Более сложная архитектура
- Потенциальные конфликты зависимостей

## Рекомендуемый подход

Рекомендую **Вариант 2** с созданием `APIManager`, который будет использовать существующий `BudgetManager`:

```python
# src/core/api_manager.py
from fastapi import FastAPI, HTTPException
from .manager import BudgetManager
from .transaction import Transaction
from pydantic import BaseModel
from typing import List, Optional

class TransactionCreate(BaseModel):
    amount: float
    category: str
    note: str
    date: str
    type_: str
    report_id: Optional[int] = None

class APIManager:
    def __init__(self):
        self.budget_manager = BudgetManager()
        self.app = FastAPI(title="Budget Tracker API")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/api/transactions")
        async def get_transactions():
            return self.budget_manager.get_transactions()
        
        @self.app.post("/api/transactions")
        async def create_transaction(transaction: TransactionCreate):
            new_transaction = Transaction(
                amount=transaction.amount,
                category=transaction.category,
                note=transaction.note,
                date=transaction.date,
                type_=transaction.type_,
                report_id=transaction.report_id
            )
            self.budget_manager.add_transaction(new_transaction)
            return {"message": "Transaction created successfully"}
```

## План реализации

### Этап 1: Базовая настройка
1. Установить FastAPI и зависимости
2. Создать базовую структуру API
3. Настроить CORS для веб-клиента

### Этап 2: Основные endpoints
1. CRUD операции для транзакций
2. API для работы с планами
3. Базовые endpoints для аналитики

### Этап 3: Расширенная функциональность
1. Импорт данных через API
2. Экспорт данных
3. Аутентификация и авторизация

### Этап 4: Веб-интерфейс
1. Создать простой HTML/CSS/JS фронтенд
2. Интегрировать с API
3. Добавить интерактивные графики

## Преимущества интеграции FastAPI

1. **Автоматическая документация** - Swagger UI из коробки
2. **Валидация данных** - Pydantic модели
3. **Типизация** - Полная поддержка типов Python
4. **Производительность** - Один из самых быстрых фреймворков
5. **Современность** - Поддержка async/await
6. **Простота тестирования** - Встроенные инструменты для тестов

## Примеры использования

### 1. Веб-приложение
```html
<!-- Простой веб-интерфейс -->
<!DOCTYPE html>
<html>
<head>
    <title>Budget Tracker Web</title>
</head>
<body>
    <div id="app">
        <h1>Мой Бюджет</h1>
        <div id="transactions"></div>
        <form id="add-transaction">
            <input type="number" placeholder="Сумма" required>
            <input type="text" placeholder="Категория" required>
            <button type="submit">Добавить</button>
        </form>
    </div>
    <script>
        // JavaScript для взаимодействия с API
        fetch('/api/transactions')
            .then(response => response.json())
            .then(data => {
                // Отображение транзакций
            });
    </script>
</body>
</html>
```

### 2. Мобильное приложение
```python
# Пример использования API в мобильном приложении
import requests

class BudgetTrackerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_transactions(self):
        response = requests.get(f"{self.base_url}/api/transactions")
        return response.json()
    
    def add_transaction(self, amount, category, note, date, type_):
        data = {
            "amount": amount,
            "category": category,
            "note": note,
            "date": date,
            "type_": type_
        }
        response = requests.post(f"{self.base_url}/api/transactions", json=data)
        return response.json()
```

### 3. Автоматический импорт
```python
# Скрипт для автоматического импорта банковских данных
import requests
from datetime import datetime

def import_bank_data():
    # Получение данных от банка (пример)
    bank_data = get_bank_transactions()
    
    for transaction in bank_data:
        requests.post("http://localhost:8000/api/transactions", json={
            "amount": transaction.amount,
            "category": transaction.category,
            "note": transaction.description,
            "date": transaction.date,
            "type_": transaction.type
        })
```

## Заключение

Интеграция FastAPI в Budget Tracker откроет множество возможностей:

- **Веб-версия** приложения для доступа с любого устройства
- **API для мобильных приложений**
- **Автоматизация** импорта данных
- **Интеграции** с внешними сервисами
- **Масштабируемость** для будущего развития

FastAPI идеально подходит для этой задачи благодаря своей простоте, производительности и современным возможностям Python.
