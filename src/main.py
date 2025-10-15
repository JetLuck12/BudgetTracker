import sys
from PyQt6.QtWidgets import QApplication
from ui.app import BudgetApp

if __name__ == "__main__":
    # Создаём объект приложения
    app = QApplication(sys.argv)

    # Создаём главное окно
    window = BudgetApp()

    # Показываем окно
    window.show()

    # Запускаем главный цикл событий
    sys.exit(app.exec())
