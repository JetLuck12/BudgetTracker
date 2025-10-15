import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
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
