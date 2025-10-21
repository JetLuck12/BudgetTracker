# Инструкция по тестированию Budget Tracker

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск базовых тестов
```bash
python run_tests_with_output.py simple
```

### 3. Просмотр результатов
- Откройте `tests/reports/test_test_basic_*.html` в браузере
- Посмотрите консольный вывод в `tests/reports/*_console.txt`

## Доступные команды

| Команда | Описание | Файл тестов |
|---------|----------|-------------|
| `simple` | Базовые тесты | `test_basic.py` |
| `quick` | Быстрые тесты | `test_core_simple.py` |
| `all` | Все тесты | Все файлы |
| `specific` | Конкретные тесты | По очереди |
| `core` | Core тесты | `test_core.py` |
| `api` | API тесты | `test_api.py` |
| `integration` | Интеграционные тесты | `test_integration.py` |

## Примеры использования

### Запуск базовых тестов
```bash
python run_tests_with_output.py simple
```

### Запуск всех тестов
```bash
python run_tests_with_output.py all
```

### Запуск конкретных тестов
```bash
python run_tests_with_output.py specific
```

## Структура отчетов

```
tests/reports/
├── test_test_basic_*.html          # HTML отчеты
├── test_test_basic_*_console.txt  # Консольные логи
├── test_test_basic_*_coverage.html/ # Отчеты покрытия
│   ├── index.html                 # Главная страница покрытия
│   ├── *.html                     # Детали по файлам
│   └── ...
└── ...
```

## Просмотр HTML отчетов

1. Откройте файл `tests/reports/test_test_basic_*.html` в браузере
2. Увидите детальные результаты тестирования
3. Для просмотра покрытия кода откройте `tests/reports/test_test_basic_*_coverage.html/index.html`

## Отладка тестов

### Запуск отладочных тестов
```bash
python -m pytest tests/test_debug.py -v -s
```

### Запуск конкретного теста
```bash
python -m pytest tests/test_basic.py::TestSummaryBasic::test_get_financial_summary_single_transaction -v
```

## Настройка

### Добавление новых тестов
1. Создайте файл `tests/test_*.py`
2. Добавьте команду в `run_tests_with_output.py`
3. Запустите тесты

### Изменение конфигурации
- `pytest.ini` - основная конфигурация pytest
- `conftest.py` - общие фикстуры
- `requirements.txt` - зависимости

## Устранение проблем

### Тесты не запускаются
```bash
# Проверьте установку зависимостей
pip install pytest pytest-html pytest-cov

# Проверьте конфигурацию
python -m pytest --version
```

### Ошибки в тестах
1. Посмотрите консольный вывод в `tests/reports/*_console.txt`
2. Запустите отладочные тесты: `python -m pytest tests/test_debug.py -v -s`
3. Проверьте логику в соответствующих файлах

### Проблемы с покрытием
1. Откройте `tests/reports/*_coverage.html/index.html`
2. Посмотрите какие файлы не покрыты тестами
3. Добавьте соответствующие тесты

## Контакты
При возникновении проблем обратитесь к `TESTING_REPORT.md` для подробной информации о решенных проблемах.
