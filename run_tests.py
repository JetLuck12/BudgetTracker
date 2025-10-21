#!/usr/bin/env python3
"""
Скрипт для запуска тестов Budget Tracker
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Запускает команду и выводит результат"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def check_dependencies():
    """Проверяет установленные зависимости"""
    print("🔍 Проверка зависимостей...")
    
    required_packages = [
        'pytest',
        'fastapi',
        'uvicorn',
        'pandas',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True


def create_directories():
    """Создает необходимые директории"""
    directories = [
        'tests/logs',
        'tests/tmp',
        'tests/.pytest_cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана директория: {directory}")


def run_tests(test_type="all", verbose=False, coverage=False):
    """Запускает тесты"""
    base_command = "python -m pytest"
    
    if verbose:
        base_command += " -v"
    
    if coverage:
        base_command += " --cov=src --cov-report=html --cov-report=term-missing"
    
    commands = {
        "all": f"{base_command} tests/",
        "unit": f"{base_command} tests/test_core.py -m unit",
        "integration": f"{base_command} tests/test_integration.py -m integration",
        "api": f"{base_command} tests/test_api.py -m api",
        "core": f"{base_command} tests/test_core.py -m core",
        "fast": f"{base_command} tests/ -m 'not slow'",
        "slow": f"{base_command} tests/ -m slow"
    }
    
    if test_type not in commands:
        print(f"❌ Неизвестный тип тестов: {test_type}")
        print(f"Доступные типы: {', '.join(commands.keys())}")
        return False
    
    command = commands[test_type]
    description = f"Запуск {test_type} тестов"
    
    return run_command(command, description)


def run_linting():
    """Запускает проверку кода"""
    commands = [
        ("python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503", "Проверка стиля кода (flake8)"),
        ("python -m black --check src/ tests/", "Проверка форматирования кода (black)"),
        ("python -m isort --check-only src/ tests/", "Проверка сортировки импортов (isort)")
    ]
    
    for command, description in commands:
        success = run_command(command, description)
        if not success:
            print(f"⚠️  {description} завершился с предупреждениями")


def generate_report():
    """Генерирует отчет о тестах"""
    print("\n📊 Генерация отчета...")
    
    # Создаем HTML отчет
    command = "python -m pytest tests/ --html=tests/reports/report.html --self-contained-html"
    run_command(command, "Генерация HTML отчета")
    
    # Создаем отчет о покрытии
    command = "python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing"
    run_command(command, "Генерация отчета о покрытии кода")


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Скрипт для запуска тестов Budget Tracker")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "api", "core", "fast", "slow"],
        default="all",
        help="Тип тестов для запуска"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Включить отчет о покрытии кода"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Запустить проверку кода"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Генерировать отчеты"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Проверить зависимости"
    )
    
    args = parser.parse_args()
    
    print("🧪 Budget Tracker Test Runner")
    print("=" * 50)
    
    # Проверяем зависимости
    if args.check_deps or args.type == "all":
        if not check_dependencies():
            sys.exit(1)
    
    # Создаем директории
    create_directories()
    
    # Запускаем проверку кода
    if args.lint:
        run_linting()
    
    # Запускаем тесты
    success = run_tests(args.type, args.verbose, args.coverage)
    
    # Генерируем отчеты
    if args.report and success:
        generate_report()
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n❌ Некоторые тесты не прошли!")
        sys.exit(1)


if __name__ == "__main__":
    main()
