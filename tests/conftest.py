"""
Конфигурация и фикстуры для тестов Budget Tracker
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock

# Добавляем путь к src для импорта модулей
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.DBManager import DBManager
from core.manager import BudgetManager
from core.transaction import Transaction
from core.summary import EXPENSE_TYPE, INCOME_TYPE


@pytest.fixture(scope="session")
def test_data_dir():
    """Фикстура для временной директории с тестовыми данными"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db_file(test_data_dir):
    """Фикстура для временного файла базы данных"""
    db_path = os.path.join(test_data_dir, "test_budget.db")
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_manager(temp_db_file):
    """Фикстура для DBManager с временной базой данных"""
    return DBManager(temp_db_file)


@pytest.fixture
def budget_manager(temp_db_file):
    """Фикстура для BudgetManager с временной базой данных"""
    with patch('core.manager.BudgetManager.DB_FILE', temp_db_file):
        manager = BudgetManager()
        return manager


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями"""
    return [
        Transaction(
            amount=2000.0,
            category="Зарплата",
            note="Зарплата за январь",
            date="2025-01-01",
            type_=INCOME_TYPE,
            report_id=1,
            id=1
        ),
        Transaction(
            amount=1000.0,
            category="Продукты",
            note="Покупка продуктов в супермаркете",
            date="2025-01-02",
            type_=EXPENSE_TYPE,
            report_id=1,
            id=2
        ),
        Transaction(
            amount=500.0,
            category="Транспорт",
            note="Заправка автомобиля",
            date="2025-01-03",
            type_=EXPENSE_TYPE,
            report_id=1,
            id=3
        ),
        Transaction(
            amount=300.0,
            category="Продукты",
            note="Покупка хлеба и молока",
            date="2025-01-04",
            type_=EXPENSE_TYPE,
            report_id=1,
            id=4
        ),
        Transaction(
            amount=200.0,
            category="Развлечения",
            note="Поход в кино",
            date="2025-01-05",
            type_=EXPENSE_TYPE,
            report_id=1,
            id=5
        )
    ]


@pytest.fixture
def populated_db_manager(db_manager, sample_transactions):
    """Фикстура для DBManager с заполненными данными"""
    for transaction in sample_transactions:
        db_manager.add_transaction(transaction)
    return db_manager


@pytest.fixture
def populated_budget_manager(budget_manager, sample_transactions):
    """Фикстура для BudgetManager с заполненными данными"""
    for transaction in sample_transactions:
        budget_manager.add_transaction(transaction)
    return budget_manager


@pytest.fixture
def mock_pandas():
    """Фикстура для мока pandas"""
    with patch('core.summary.pd') as mock_pd:
        yield mock_pd


@pytest.fixture
def mock_file_operations():
    """Фикстура для мока файловых операций"""
    with patch('builtins.open', create=True) as mock_open:
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs'):
                yield mock_open


@pytest.fixture
def sample_csv_content():
    """Фикстура с содержимым тестового CSV файла"""
    return """Дата операции,Номер счета,Описание операции,Сумма,Категория,Тип,Комментарий,Кэшбэк
2025-01-01,1234567890,Покупка в супермаркете,1000.0,Продукты,Списание,Покупка продуктов,0
2025-01-02,1234567890,Заправка автомобиля,500.0,Транспорт,Списание,Заправка,0
2025-01-03,1234567890,Зарплата,2000.0,Зарплата,Пополнение,Зарплата за январь,0
2025-01-04,1234567890,Поход в кино,200.0,Развлечения,Списание,Кинотеатр,0"""


@pytest.fixture
def sample_excel_content():
    """Фикстура с содержимым тестового Excel файла"""
    # Это заглушка, реальный Excel файл будет создан в тестах
    return b"fake excel content"


@pytest.fixture
def sample_plan_data():
    """Фикстура с тестовыми данными плана"""
    return {
        "Продукты": 5000.0,
        "Транспорт": 2000.0,
        "Развлечения": 1000.0,
        "Одежда": 1500.0,
        "Медицина": 800.0
    }


@pytest.fixture
def sample_plan_json():
    """Фикстура с JSON данными плана"""
    return [
        {"category": "Продукты", "plan_expense": 5000.0},
        {"category": "Транспорт", "plan_expense": 2000.0},
        {"category": "Развлечения", "plan_expense": 1000.0},
        {"category": "Одежда", "plan_expense": 1500.0},
        {"category": "Медицина", "plan_expense": 800.0}
    ]


@pytest.fixture
def mock_datetime():
    """Фикстура для мока datetime"""
    with patch('core.DBManager.datetime') as mock_dt:
        mock_dt.now.return_value.strftime.return_value = "2025-01-01 12:00:00"
        yield mock_dt


@pytest.fixture
def mock_threading_local():
    """Фикстура для мока threading.local"""
    with patch('core.DBManager.threading.local') as mock_local:
        mock_local_instance = MagicMock()
        mock_local.return_value = mock_local_instance
        mock_local_instance.conn = MagicMock()
        yield mock_local_instance


class TestDataFactory:
    """Фабрика для создания тестовых данных"""
    
    @staticmethod
    def create_transaction(amount=1000.0, category="Тест", note="Тестовая транзакция", 
                          date="2025-01-01", type_=EXPENSE_TYPE, report_id=1, id=None):
        """Создает тестовую транзакцию"""
        return Transaction(
            amount=amount,
            category=category,
            note=note,
            date=date,
            type_=type_,
            report_id=report_id,
            id=id
        )
    
    @staticmethod
    def create_income_transaction(amount=2000.0, category="Зарплата", note="Зарплата"):
        """Создает транзакцию дохода"""
        return TestDataFactory.create_transaction(
            amount=amount,
            category=category,
            note=note,
            type_=INCOME_TYPE
        )
    
    @staticmethod
    def create_expense_transaction(amount=500.0, category="Продукты", note="Покупка продуктов"):
        """Создает транзакцию расхода"""
        return TestDataFactory.create_transaction(
            amount=amount,
            category=category,
            note=note,
            type_=EXPENSE_TYPE
        )
    
    @staticmethod
    def create_transaction_list(count=5):
        """Создает список тестовых транзакций"""
        transactions = []
        categories = ["Продукты", "Транспорт", "Развлечения", "Одежда", "Медицина"]
        
        for i in range(count):
            transaction = TestDataFactory.create_transaction(
                amount=1000.0 + i * 100,
                category=categories[i % len(categories)],
                note=f"Тестовая транзакция {i+1}",
                date=f"2025-01-{i+1:02d}",
                id=i+1
            )
            transactions.append(transaction)
        
        return transactions


@pytest.fixture
def test_data_factory():
    """Фикстура для фабрики тестовых данных"""
    return TestDataFactory


# Конфигурация pytest
def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов"""
    for item in items:
        # Автоматически помечаем тесты как unit тесты
        if "test_" in item.name and not any(mark in item.name for mark in ["integration", "slow"]):
            item.add_marker(pytest.mark.unit)
        
        # Помечаем тесты с базой данных как integration
        if any(keyword in item.name for keyword in ["db", "database", "manager", "api"]):
            item.add_marker(pytest.mark.integration)


# Настройки для отображения тестов
def pytest_runtest_setup(item):
    """Настройка перед запуском теста"""
    print(f"\nЗапуск теста: {item.name}")


def pytest_runtest_teardown(item):
    """Очистка после запуска теста"""
    pass
