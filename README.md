# 💸 Budget Tracker

**Персональный трекер бюджета с поддержкой PyQt6 GUI и FastAPI веб-интерфейса**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-green.svg)](https://fastapi.tiangolo.com)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-red.svg)](https://pypi.org/project/PyQt6/)
[![SQLite](https://img.shields.io/badge/SQLite-3+-lightblue.svg)](https://sqlite.org)

## 📋 Содержание

- [Описание](#-описание)
- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Установка](#-установка)
- [Использование](#-использование)
- [API Документация](#-api-документация)
- [Структура проекта](#-структура-проекта)
- [Разработка](#-разработка)
- [Лицензия](#-лицензия)

## 🎯 Описание

Budget Tracker - это полнофункциональное приложение для управления личным бюджетом, которое предоставляет два интерфейса:

- **Desktop приложение** на PyQt6 для локального использования
- **Web API** на FastAPI для интеграции с веб-клиентами и мобильными приложениями

Приложение позволяет отслеживать доходы и расходы, анализировать финансовые данные, создавать планы бюджета и импортировать данные из банковских отчетов.

## ✨ Возможности

### 💰 Управление транзакциями
- ➕ Добавление доходов и расходов
- 🗑️ Удаление отдельных транзакций
- 📊 Просмотр всех транзакций с фильтрацией
- 🔄 Поддержка отмены/повтора операций

### 📈 Аналитика и отчеты
- 📊 Финансовая сводка (доходы, расходы, баланс)
- 📅 Анализ расходов по дням недели
- 🏆 Топ категории расходов
- 📈 График изменения баланса во времени
- 📋 Сводка по категориям

### 📋 Планирование бюджета
- 🎯 Создание планов расходов по категориям
- 📊 Сравнение планов с фактическими расходами
- 💾 Сохранение и загрузка планов

### 📥 Импорт данных
- 📄 Импорт из CSV файлов
- 📊 Импорт из Excel файлов
- 🏦 Поддержка банковских отчетов

### 🌐 Веб-интерфейс
- 🖥️ Современный веб-клиент
- 📱 Адаптивный дизайн
- 🔄 Реальное время обновления данных
- 📊 Интерактивные графики

## 🏗️ Архитектура

```
Budget Tracker
├── Desktop App (PyQt6)     # Локальное приложение
├── Web API (FastAPI)       # REST API сервер
├── Web Client (HTML/JS)    # Веб-интерфейс
└── Core Logic (Python)     # Общая бизнес-логика
```

### Компоненты системы:

- **Core** - Бизнес-логика и работа с данными
- **UI** - PyQt6 интерфейс для desktop приложения
- **API** - FastAPI сервер для веб-интеграции
- **Web Client** - HTML/JavaScript клиент

## 🚀 Установка

### Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd budget_tracker
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Проверка установки

```bash
python -c "import fastapi, uvicorn, pandas; print('✅ Все зависимости установлены')"
```

## 💻 Использование

### Desktop приложение (PyQt6)

```bash
# Запуск desktop приложения
python src/main.py

# Или через bat файл (Windows)
run.bat
```

### Web API сервер

```bash
# Запуск API сервера
python run_api.py

# Или через bat файл (Windows)
run_api.bat

# Или напрямую через uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Веб-клиент

После запуска API сервера откройте в браузере:
- **Главная страница**: http://localhost:8000/
- **Веб-клиент**: http://localhost:8000/web_client.html
- **API документация**: http://localhost:8000/docs

## 📚 API Документация

### Основные эндпоинты

#### Транзакции
- `GET /api/transactions` - Получить все транзакции
- `POST /api/transactions` - Создать новую транзакцию
- `DELETE /api/transactions/{id}` - Удалить транзакцию
- `GET /api/transactions/summary` - Финансовая сводка
- `GET /api/transactions/categories` - Список категорий

#### Аналитика
- `GET /api/analytics/summary` - Общая финансовая сводка
- `GET /api/analytics/full` - Полная аналитика
- `GET /api/analytics/weekday` - Расходы по дням недели
- `GET /api/analytics/top-categories` - Топ категории расходов
- `GET /api/analytics/graph` - Данные для графика

#### Планирование
- `GET /api/plan` - Получить план бюджета
- `POST /api/plan` - Создать план бюджета

#### Импорт
- `POST /api/import/csv` - Импорт из CSV
- `POST /api/import/excel` - Импорт из Excel

### Примеры использования

#### Получение транзакций
```bash
curl -X GET "http://localhost:8000/api/transactions"
```

#### Создание транзакции
```bash
curl -X POST "http://localhost:8000/api/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.0,
    "category": "Продукты",
    "note": "Покупка продуктов",
    "date": "2025-01-01",
    "type": "Списание"
  }'
```

#### Получение аналитики
```bash
curl -X GET "http://localhost:8000/api/analytics/summary"
```

## 📁 Структура проекта

```
budget_tracker/
├── src/                          # Исходный код
│   ├── core/                     # Бизнес-логика
│   │   ├── DBManager.py          # Управление базой данных
│   │   ├── manager.py            # Основной менеджер
│   │   ├── transaction.py        # Модель транзакции
│   │   ├── summary.py           # Аналитика и отчеты
│   │   ├── plan.py              # Планирование бюджета
│   │   └── parser.py            # Парсер файлов
│   ├── ui/                       # PyQt6 интерфейс
│   │   ├── app.py               # Главное окно
│   │   ├── tabs/                # Вкладки приложения
│   │   └── views/               # Представления
│   ├── api/                      # FastAPI сервер
│   │   ├── main.py              # Основное приложение
│   │   ├── models.py            # Pydantic модели
│   │   ├── dependencies.py      # Зависимости
│   │   └── routers/             # API маршруты
│   └── main.py                  # Точка входа PyQt6
├── data/                         # Данные приложения
│   └── budget.db                # База данных SQLite
├── tests/                        # Тесты
├── web_client.html              # Веб-клиент
├── requirements.txt             # Зависимости Python
├── run_api.py                   # Скрипт запуска API
├── run_api.bat                  # Bat файл для Windows
└── README.md                    # Этот файл
```

## 🔧 Разработка

### Настройка окружения разработки

```bash
# Клонирование репозитория
git clone <repository-url>
cd budget_tracker

# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Тестирование

```bash
# Запуск тестов
python -m pytest tests/

# Запуск конкретного теста
python tests/test_core.py
```

### Структура базы данных

#### Таблица `transactions`
- `id` - Уникальный идентификатор
- `report_id` - ID отчета
- `amount` - Сумма транзакции
- `category` - Категория
- `note` - Описание
- `date` - Дата
- `type` - Тип (Списание/Пополнение)

#### Таблица `reports`
- `id` - Уникальный идентификатор
- `filename` - Имя файла
- `import_date` - Дата импорта

### Добавление новых функций

1. **Для API**: Добавьте новый роутер в `src/api/routers/`
2. **Для UI**: Добавьте новую вкладку в `src/ui/tabs/`
3. **Для бизнес-логики**: Расширьте классы в `src/core/`

## 🐛 Решение проблем

### Частые проблемы

#### SQLite threading ошибки
```
SQLite objects created in a thread can only be used in that same thread
```
**Решение**: Используйте thread-safe подключения (уже исправлено в коде)

#### Ошибки импорта модулей
```
ModuleNotFoundError: No module named 'src'
```
**Решение**: Убедитесь, что запускаете из корневой директории проекта

#### Порт уже используется
```
Address already in use: 8000
```
**Решение**: Измените порт или остановите другой процесс на порту 8000

### Логи и отладка

```bash
# Запуск с подробными логами
uvicorn src.api.main:app --reload --log-level debug

# Проверка статуса API
curl http://localhost:8000/health
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для получения дополнительной информации.

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте [Issues](https://github.com/your-repo/budget_tracker/issues)
2. Создайте новый Issue с подробным описанием проблемы
3. Приложите логи и скриншоты, если возможно

## 🎉 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) - Современный веб-фреймворк для Python
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI фреймворк
- [SQLite](https://sqlite.org/) - Встроенная база данных
- [Pandas](https://pandas.pydata.org/) - Анализ данных
- [Pydantic](https://pydantic.dev/) - Валидация данных

---

**Сделано с ❤️ для управления личными финансами**