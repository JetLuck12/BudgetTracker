#!/usr/bin/env python3
"""
Скрипт для запуска тестов Budget Tracker с сохранением результатов
"""
import os
import sys
import subprocess
import datetime
from pathlib import Path


def create_reports_directory():
    """Создает директорию для отчетов"""
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def run_tests_with_output(test_file=None, output_format="html"):
    """Запускает тесты и сохраняет результаты"""
    reports_dir = create_reports_directory()
    
    # Генерируем имя файла с timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if test_file:
        base_name = f"test_{Path(test_file).stem}_{timestamp}"
    else:
        base_name = f"all_tests_{timestamp}"
    
    # Команда для запуска тестов
    if test_file:
        cmd = f"python -m pytest {test_file} -v"
    else:
        cmd = "python -m pytest tests/ -v"
    
    # Добавляем формат вывода
    if output_format == "html":
        html_file = reports_dir / f"{base_name}.html"
        cmd += f" --html={html_file} --self-contained-html"
    elif output_format == "json":
        json_file = reports_dir / f"{base_name}.json"
        cmd += f" --json-report --json-report-file={json_file}"
    
    # Добавляем покрытие кода
    coverage_file = reports_dir / f"{base_name}_coverage.html"
    cmd += f" --cov=src --cov-report=html:{coverage_file} --cov-report=term-missing"
    
    # Добавляем детальный вывод
    cmd += " --tb=short"
    
    print(f"🚀 Запуск тестов: {cmd}")
    print(f"📁 Результаты будут сохранены в: {reports_dir}")
    
    # Запускаем тесты
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Сохраняем консольный вывод
        console_file = reports_dir / f"{base_name}_console.txt"
        with open(console_file, 'w', encoding='utf-8') as f:
            f.write(f"Команда: {cmd}\n")
            f.write(f"Время запуска: {datetime.datetime.now()}\n")
            f.write("="*80 + "\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\nКод возврата: {result.returncode}\n")
        
        print(f"✅ Тесты завершены с кодом: {result.returncode}")
        print(f"📄 Консольный вывод сохранен в: {console_file}")
        
        if output_format == "html":
            print(f"🌐 HTML отчет: {html_file}")
        if output_format == "json":
            print(f"📊 JSON отчет: {json_file}")
        
        print(f"📈 Отчет о покрытии: {coverage_file}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False


def run_specific_tests():
    """Запускает конкретные тесты"""
    test_files = [
        "tests/test_core_simple.py",
        "tests/test_core.py", 
        "tests/test_api.py",
        "tests/test_integration.py"
    ]
    
    reports_dir = create_reports_directory()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n{'='*60}")
            print(f"🧪 Запуск тестов: {test_file}")
            print(f"{'='*60}")
            
            success = run_tests_with_output(test_file, "html")
            results[test_file] = success
            
            if success:
                print(f"✅ {test_file} - ПРОШЕЛ")
            else:
                print(f"❌ {test_file} - НЕ ПРОШЕЛ")
        else:
            print(f"⚠️  Файл не найден: {test_file}")
            results[test_file] = False
    
    # Создаем сводный отчет
    summary_file = reports_dir / f"test_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Сводный отчет тестирования\n")
        f.write(f"Время: {datetime.datetime.now()}\n")
        f.write("="*50 + "\n\n")
        
        for test_file, success in results.items():
            status = "✅ ПРОШЕЛ" if success else "❌ НЕ ПРОШЕЛ"
            f.write(f"{test_file}: {status}\n")
        
        f.write(f"\nВсего тестов: {len(results)}\n")
        f.write(f"Прошло: {sum(results.values())}\n")
        f.write(f"Не прошло: {len(results) - sum(results.values())}\n")
    
    print(f"\n📋 Сводный отчет сохранен в: {summary_file}")
    
    return all(results.values())


def run_quick_tests():
    """Запускает быстрые тесты"""
    print("⚡ Запуск быстрых тестов...")
    
    # Запускаем только простые тесты
    cmd = "python -m pytest tests/test_core_simple.py -v --tb=short"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Сохраняем результат
        reports_dir = create_reports_directory()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        quick_file = reports_dir / f"quick_tests_{timestamp}.txt"
        
        with open(quick_file, 'w', encoding='utf-8') as f:
            f.write(f"Быстрые тесты - {datetime.datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result.stdout)
            f.write("\n" + "="*50 + "\n")
            f.write(result.stderr)
        
        print(f"📄 Результат сохранен в: {quick_file}")
        print(f"✅ Код возврата: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Основная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick":
            success = run_quick_tests()
        elif command == "all":
            success = run_tests_with_output()
        elif command == "specific":
            success = run_specific_tests()
        elif command == "simple":
            success = run_tests_with_output("tests/test_basic.py")
        elif command == "core":
            success = run_tests_with_output("tests/test_core.py")
        elif command == "api":
            success = run_tests_with_output("tests/test_api.py")
        elif command == "integration":
            success = run_tests_with_output("tests/test_integration.py")
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("Доступные команды: quick, all, specific, simple, core, api, integration")
            sys.exit(1)
    else:
        print("🧪 Budget Tracker Test Runner")
        print("=" * 50)
        print("Использование:")
        print("  python run_tests_with_output.py quick      - Быстрые тесты")
        print("  python run_tests_with_output.py all        - Все тесты")
        print("  python run_tests_with_output.py specific   - Конкретные тесты")
        print("  python run_tests_with_output.py simple     - Простые тесты")
        print("  python run_tests_with_output.py core       - Core тесты")
        print("  python run_tests_with_output.py api        - API тесты")
        print("  python run_tests_with_output.py integration - Интеграционные тесты")
        print("\nПример:")
        print("  python run_tests_with_output.py quick")
        return
    
    if success:
        print("\n🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n💥 Некоторые тесты не прошли!")
        sys.exit(1)


if __name__ == "__main__":
    main()
