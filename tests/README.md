# 🧪 Тесты для Budget Tracker

Этот документ описывает тестовую инфраструктуру проекта Budget Tracker.

## 📋 Содержание

- [Обзор](#-обзор)
- [Структура тестов](#-структура-тестов)
- [Запуск тестов](#-запуск-тестов)
- [Типы тестов](#-типы-тестов)
- [Конфигурация](#-конфигурация)
- [Фикстуры](#-фикстуры)
- [Покрытие кода](#-покрытие-кода)
- [Отчеты](#-отчеты)

## 🎯 Обзор

Проект Budget Tracker включает комплексную тестовую инфраструктуру, покрывающую:

- **Core модули** - бизнес-логика и работа с данными
- **API эндпоинты** - REST API функциональность
- **Интеграционные тесты** - полные workflow
- **Edge cases** - граничные условия и обработка ошибок

## 📁 Структура тестов

```
tests/
├── conftest.py              # Конфигурация и фикстуры
├── test_core.py             # Тесты core модулей
├── test_api.py              # Тесты API эндпоинтов
├── test_integration.py      # Интеграционные тесты
├── logs/                    # Логи тестов
├── tmp/                     # Временные файлы
└── reports/                 # Отчеты о тестах
```

## 🚀 Запуск тестов

### Быстрый запуск

```bash
# Запуск всех тестов
python run_tests.py

# Запуск с подробным выводом
python run_tests.py --verbose

# Запуск с отчетом о покрытии
python run_tests.py --coverage
```

### Прямой запуск через pytest

```bash
# Все тесты
pytest tests/

# Конкретный файл
pytest tests/test_core.py

# Конкретный тест
pytest tests/test_core.py::TestTransaction::test_transaction_creation

# С подробным выводом
pytest tests/ -v

# Только быстрые тесты
pytest tests/ -m "not slow"
```

### Запуск через скрипт

```bash
# Различные типы тестов
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type api
python run_tests.py --type fast
python run_tests.py --type slow

# Проверка кода
python run_tests.py --lint

# Генерация отчетов
python run_tests.py --report
```

## 🏷️ Типы тестов

### Unit тесты (`test_core.py`)

Тестируют отдельные компоненты в изоляции:

- **Transaction** - создание и валидация транзакций
- **DBManager** - операции с базой данных
- **Summary** - аналитика и расчеты
- **BudgetManager** - основная бизнес-логика

```python
def test_transaction_creation(self):
    """Тест создания транзакции"""
    transaction = Transaction(
        amount=1000.0,
        category="Продукты",
        note="Покупка продуктов",
        date="2025-01-01",
        type_=EXPENSE_TYPE,
        report_id=1
    )
    
    assert transaction.amount == 1000.0
    assert transaction.category == "Продукты"
```

### API тесты (`test_api.py`)

Тестируют REST API эндпоинты:

- **Transactions API** - CRUD операции с транзакциями
- **Analytics API** - получение аналитики
- **Plan API** - управление планами бюджета
- **Import API** - импорт данных

```python
def test_get_transactions(self, client, mock_budget_manager):
    """Тест получения транзакций"""
    mock_budget_manager.get_transactions.return_value = []
    
    response = client.get("/api/transactions")
    
    assert response.status_code == 200
    assert response.json() == []
```

### Интеграционные тесты (`test_integration.py`)

Тестируют полные workflow:

- **Полный цикл** - от добавления транзакций до получения аналитики
- **Edge cases** - граничные условия
- **Обработка ошибок** - некорректные данные
- **Производительность** - большие объемы данных

```python
def test_full_workflow(self, temp_db_file):
    """Тест полного workflow приложения"""
    with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
        manager = BudgetManager()
    
    # Добавляем транзакции
    transactions = [
        Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, -1),
        Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", EXPENSE_TYPE, -1)
    ]
    
    for transaction in transactions:
        manager.add_transaction(transaction)
    
    # Проверяем результат
    summary = manager.get_financial_summary()
    assert summary["balance"] == 1000.0
```

## ⚙️ Конфигурация

### pytest.ini

Основные настройки pytest:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
```

### Маркеры тестов

- `@pytest.mark.unit` - unit тесты
- `@pytest.mark.integration` - интеграционные тесты
- `@pytest.mark.api` - API тесты
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.core` - тесты core модулей

## 🔧 Фикстуры

### Основные фикстуры (`conftest.py`)

```python
@pytest.fixture
def temp_db_file(test_data_dir):
    """Фикстура для временного файла базы данных"""
    db_path = os.path.join(test_data_dir, "test_budget.db")
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями"""
    return [
        Transaction(2000.0, "Зарплата", "Зарплата", "2025-01-01", INCOME_TYPE, 1, id=1),
        Transaction(1000.0, "Продукты", "Покупка", "2025-01-02", EXPENSE_TYPE, 1, id=2)
    ]
```

### Использование фикстур

```python
def test_with_fixtures(self, db_manager, sample_transactions):
    """Тест с использованием фикстур"""
    for transaction in sample_transactions:
        db_manager.add_transaction(transaction)
    
    transactions = db_manager.get_transactions()
    assert len(transactions) == 2
```

## 📊 Покрытие кода

### Установка pytest-cov

```bash
pip install pytest-cov
```

### Запуск с покрытием

```bash
# Консольный отчет
pytest tests/ --cov=src --cov-report=term-missing

# HTML отчет
pytest tests/ --cov=src --cov-report=html

# Через скрипт
python run_tests.py --coverage
```

### Результат покрытия

```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/core/DBManager.py      45      2    96%   23, 45
src/core/manager.py        89      5    94%   45-49
src/core/summary.py        67      3    96%   12, 34, 56
src/core/transaction.py    25      0   100%
-----------------------------------------------------
TOTAL                     226     10    96%
```

## 📈 Отчеты

### HTML отчеты

```bash
# Генерация HTML отчета
pytest tests/ --html=tests/reports/report.html --self-contained-html

# Через скрипт
python run_tests.py --report
```

### Структура отчетов

```
tests/reports/
├── report.html              # HTML отчет о тестах
├── coverage_html/           # HTML отчет о покрытии
│   └── index.html
└── coverage.xml            # XML отчет о покрытии
```

## 🐛 Отладка тестов

### Подробный вывод

```bash
# Максимально подробный вывод
pytest tests/ -vvv --tb=long

# Остановка на первой ошибке
pytest tests/ -x

# Запуск только упавших тестов
pytest tests/ --lf
```

### Логирование

```bash
# Включение логов
pytest tests/ --log-cli-level=DEBUG

# Логи в файл
pytest tests/ --log-file=tests/logs/debug.log
```

### Отладка конкретного теста

```python
def test_debug_example(self):
    """Пример отладочного теста"""
    import pdb; pdb.set_trace()  # Точка останова
    # или
    breakpoint()  # Python 3.7+
```

## 🔍 Проверка кода

### Установка инструментов

```bash
pip install flake8 black isort
```

### Запуск проверки

```bash
# Проверка стиля
flake8 src/ tests/ --max-line-length=100

# Форматирование
black src/ tests/

# Сортировка импортов
isort src/ tests/

# Через скрипт
python run_tests.py --lint
```

## 📝 Написание тестов

### Структура теста

```python
class TestComponent:
    """Тесты для компонента"""
    
    def test_basic_functionality(self):
        """Тест базовой функциональности"""
        # Arrange - подготовка данных
        data = {"key": "value"}
        
        # Act - выполнение действия
        result = function_under_test(data)
        
        # Assert - проверка результата
        assert result == expected_result
    
    def test_edge_case(self):
        """Тест граничного случая"""
        with pytest.raises(ValueError):
            function_under_test(None)
```

### Лучшие практики

1. **Именование** - описательные имена тестов
2. **Изоляция** - каждый тест независим
3. **Фикстуры** - переиспользование данных
4. **Моки** - изоляция зависимостей
5. **Покрытие** - тестирование всех путей

### Примеры

```python
# Тест с параметрами
@pytest.mark.parametrize("amount,expected", [
    (1000.0, 1000.0),
    (0.0, 0.0),
    (-100.0, -100.0)
])
def test_amount_validation(self, amount, expected):
    transaction = Transaction(amount=amount, ...)
    assert transaction.amount == expected

# Тест с моками
@patch('core.summary.pd')
def test_with_mock(self, mock_pd):
    mock_pd.DataFrame.return_value = mock_df
    result = Summary.get_summary_by_weekday(transactions)
    assert isinstance(result, dict)
```

## 🚀 CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py --coverage
```

## 📚 Дополнительные ресурсы

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)

---

**Сделано с ❤️ для качественного тестирования Budget Tracker**
