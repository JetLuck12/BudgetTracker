# 🚀 FastAPI Integration для Budget Tracker

## Обзор

Этот проект теперь включает в себя полноценный REST API на базе FastAPI, который позволяет управлять бюджетом через веб-интерфейс, мобильные приложения или любые другие клиенты.

## 🏗️ Архитектура

```
src/
├── core/           # Существующая бизнес-логика
├── ui/            # PyQt6 интерфейс (существующий)
├── api/            # FastAPI сервер (новый)
│   ├── main.py     # Основное приложение FastAPI
│   ├── models.py   # Pydantic модели
│   ├── dependencies.py # Зависимости
│   └── routers/    # API маршруты
│       ├── transactions.py
│       ├── plan.py
│       ├── analytics.py
│       └── import.py
└── main.py        # Точка входа PyQt6
```

## 📦 Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🚀 Запуск API сервера

### Способ 1: Через Python скрипт
```bash
python run_api.py
```

### Способ 2: Через bat файл (Windows)
```bash
run_api.bat
```

### Способ 3: Напрямую через uvicorn
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Документация API

После запуска сервера документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Главная страница**: http://localhost:8000

## 🌐 Веб-клиент

Откройте файл `web_client.html` в браузере для использования веб-интерфейса.

## 📡 API Endpoints

### Транзакции

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/transactions` | Получить все транзакции |
| POST | `/api/transactions` | Создать новую транзакцию |
| DELETE | `/api/transactions/{id}` | Удалить транзакцию |
| GET | `/api/transactions/summary` | Получить сводку по транзакциям |
| GET | `/api/transactions/categories` | Получить все категории |

### Планы бюджета

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/plan` | Получить текущий план |
| POST | `/api/plan` | Создать новый план |
| PUT | `/api/plan` | Обновить план |
| GET | `/api/plan/progress` | Получить прогресс выполнения плана |

### Аналитика

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/analytics/summary` | Общая финансовая сводка |
| GET | `/api/analytics/categories` | Сводка по категориям |
| GET | `/api/analytics/weekday` | Расходы по дням недели |
| GET | `/api/analytics/top-categories` | Топ категории расходов |
| GET | `/api/analytics/graph` | Данные для графика |
| GET | `/api/analytics/full` | Полная аналитика |

### Импорт данных

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/import/csv` | Импорт из CSV файла |
| POST | `/api/import/excel` | Импорт из Excel файла |

## 💡 Примеры использования

### 1. Получение всех транзакций

```bash
curl -X GET "http://localhost:8000/api/transactions"
```

### 2. Создание новой транзакции

```bash
curl -X POST "http://localhost:8000/api/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.0,
    "category": "Продукты",
    "note": "Покупка в супермаркете",
    "date": "2024-01-15",
    "type": "Списание"
  }'
```

### 3. Получение финансовой сводки

```bash
curl -X GET "http://localhost:8000/api/analytics/summary"
```

### 4. Импорт CSV файла

```bash
curl -X POST "http://localhost:8000/api/import/csv" \
  -F "file=@transactions.csv"
```

## 🔧 Настройка

### Изменение порта

Отредактируйте файл `run_api.py`:

```python
uvicorn.run(
    "src.api.main:app",
    host="0.0.0.0",
    port=8080,  # Измените порт здесь
    reload=True,
    log_level="info"
)
```

### Настройка CORS

В файле `src/api/main.py` измените настройки CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешить только определенные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🧪 Тестирование

### Тест через curl

```bash
# Проверка здоровья API
curl -X GET "http://localhost:8000/health"

# Получение транзакций
curl -X GET "http://localhost:8000/api/transactions"

# Создание транзакции
curl -X POST "http://localhost:8000/api/transactions" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "category": "Тест", "note": "Тестовая транзакция", "date": "2024-01-01", "type": "Списание"}'
```

### Тест через Python

```python
import requests

# Получение транзакций
response = requests.get("http://localhost:8000/api/transactions")
print(response.json())

# Создание транзакции
data = {
    "amount": 100.0,
    "category": "Тест",
    "note": "Тестовая транзакция",
    "date": "2024-01-01",
    "type": "Списание"
}
response = requests.post("http://localhost:8000/api/transactions", json=data)
print(response.json())
```

## 🔒 Безопасность

⚠️ **Важно**: Текущая реализация не включает аутентификацию. Для продакшена рекомендуется добавить:

1. JWT токены
2. API ключи
3. Rate limiting
4. HTTPS

## 🚀 Развертывание

### Локальная разработка
```bash
uvicorn src.api.main:app --reload
```

### Продакшен
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (опционально)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📱 Интеграции

API можно использовать для:

- **Веб-приложений** (React, Vue, Angular)
- **Мобильных приложений** (React Native, Flutter)
- **Десктопных приложений** (Electron)
- **Автоматизации** (Python скрипты)
- **Интеграций с банками** (Open Banking API)

## 🐛 Отладка

### Логи
Сервер выводит подробные логи в консоль. Для изменения уровня логирования измените параметр `log_level` в `run_api.py`.

### Проверка состояния
```bash
curl -X GET "http://localhost:8000/health"
```

### Проверка документации
Откройте http://localhost:8000/docs в браузере для интерактивной документации.

## 📈 Мониторинг

Рекомендуется добавить:

- Prometheus метрики
- Health checks
- Логирование запросов
- Мониторинг производительности

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

Этот проект использует ту же лицензию, что и основной Budget Tracker.
