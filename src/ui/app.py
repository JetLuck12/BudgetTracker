import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence, QKeyEvent
from core.manager import BudgetManager
from ui.tabs.transactions_tab import TransactionsTab
from ui.tabs.statistics_tab import StatisticsTab
from ui.styles import APP_STYLE
from ui.tabs.plan_tab import PlanTab

class BudgetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = BudgetManager()
        self.setWindowTitle("💸 Budget Tracker")
        self.showMaximized()
        self.setStyleSheet(APP_STYLE)

        self.tabs = QTabWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        # Вкладки
        self.transactions_tab = TransactionsTab(self.manager)
        self.statistics_tab = StatisticsTab(self.manager)
        self.plan_tab = PlanTab(self.manager)

        self.tabs.addTab(self.transactions_tab, "Транзакции")
        self.tabs.addTab(self.statistics_tab, "Статистика")
        self.tabs.addTab(self.plan_tab, "План")
        
        # Настраиваем горячие клавиши
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # Ctrl+Z для отмены
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_action)
        
        # Ctrl+Y для повтора (стандартная комбинация)
        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.redo_action)
        
        # Дополнительно: Ctrl+Shift+Z для повтора
        redo_shortcut2 = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_shortcut2.activated.connect(self.redo_action)


    def undo_action(self):
        """Обработчик для Ctrl+Z - отмена последнего действия"""
        if self.manager.undo():
            # Обновляем интерфейс после отмены
            self.refresh_all_tabs()
            print("✅ Действие отменено")

    def redo_action(self):
        """Обработчик для Ctrl+Y/Ctrl+Shift+Z/F4 - повтор отменённого действия"""
        if self.manager.redo():
            # Обновляем интерфейс после повтора
            self.refresh_all_tabs()
            print("✅ Действие повторено")

    def refresh_all_tabs(self):
        """Обновляет все вкладки после изменений"""
        # Обновляем вкладку транзакций
        if hasattr(self.transactions_tab, 'refresh_transactions'):
            self.transactions_tab.refresh_transactions()
        
        # Обновляем вкладку статистики
        if hasattr(self.statistics_tab, 'refresh_statistics'):
            self.statistics_tab.refresh_statistics()
        
        # Обновляем вкладку плана
        if hasattr(self.plan_tab, 'refresh_plan'):
            self.plan_tab.refresh_plan()
            # Обновляем текущее состояние плана после изменений
            self.plan_tab.current_plan_state = self.manager.get_current_plan_state()
        
        # Сбрасываем флаг после обновления всех вкладок
        self.manager.is_undoing_redoing = False

    def keyPressEvent(self, event: QKeyEvent):
        """Обработка событий клавиатуры для дополнительной поддержки горячих клавиш"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
            # Ctrl+Z - отмена
            self.undo_action()
            event.accept()
        elif ((event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and 
               event.key() == Qt.Key.Key_Z) or
              (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Y)):
            # Ctrl+Shift+Z или Ctrl+Y - повтор
            self.redo_action()
            event.accept()
        else:
            super().keyPressEvent(event)
