from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates

class StatisticsTab(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        self.refresh_statistics()


    def init_ui(self):
        self.layout = QVBoxLayout(self)
        title = QLabel("📊 Общие показатели")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.layout.addWidget(title)

        self.balance_label = QLabel("Баланс: 0")
        self.income_label = QLabel("Доходы: 0")
        self.expense_label = QLabel("Расходы: 0")
        for w in [self.balance_label, self.income_label, self.expense_label]:
            self.layout.addWidget(w)
        # === Блок графиков (Рост баланса + Средние траты) ===
        graphs_layout = QHBoxLayout()

        # ==== График роста баланса ====
        balance_container = QVBoxLayout()
        balance_title = QLabel("📈 Рост баланса")
        balance_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        balance_container.addWidget(balance_title)

        self.balance_fig = plt.Figure(figsize=(5, 3))
        self.balance_canvas = FigureCanvas(self.balance_fig)
        balance_container.addWidget(self.balance_canvas)

        # ==== Средние траты по дням недели ====
        weekday_container = QVBoxLayout()
        weekday_title = QLabel("📆 Средние траты по дням недели")
        weekday_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        weekday_container.addWidget(weekday_title)

        self.weekday_fig = plt.Figure(figsize=(5, 3))
        self.weekday_canvas = FigureCanvas(self.weekday_fig)
        weekday_container.addWidget(self.weekday_canvas)

        # Добавляем оба блока в горизонтальный layout
        graphs_layout.addLayout(balance_container)
        graphs_layout.addLayout(weekday_container)

        self.layout.addLayout(graphs_layout)

        # === 3. Топ-5 категорий расходов ===
        self.top_fig = Figure(figsize=(4, 4))

        self.top_canvas = FigureCanvas(self.top_fig)
        self.layout.addWidget(self.top_canvas)

    def refresh_statistics(self):
        stats = self.manager.get_financial_summary()
        if "balance" in stats and "income" in stats and "expense" in stats:
            self.balance_label.setText(f"Баланс: {stats["balance"]} ₽")
            self.income_label.setText(f"Доходы: {stats["income"]} ₽")
            self.expense_label.setText(f"Расходы: {abs(stats["expense"])} ₽")

        # --- График роста баланса ---
        graph = self.manager.get_graph_summary()
        if len(graph) != 2:
            return
        dates, balances = self.manager.get_graph_summary()

        if len(dates) > 0:
            self.balance_fig.clear()
            ax = self.balance_fig.add_subplot(111)
            ax.plot(dates, balances, color="green", linewidth=2, marker="o")
            ax.set_title("Рост баланса во времени")
            ax.set_xlabel("Дата")
            ax.set_ylabel("Баланс, ₽")
            ax.grid(True, linestyle="--", alpha=0.5)

            # --- форматирование дат ---
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())

            # --- наклон подписей оси X ---
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha("right")

            self.balance_fig.tight_layout()
            self.balance_canvas.draw()

        # --- Средние траты по дням недели ---
        weekdays, expenses = self.manager.get_expenses_by_weekday()

        self.weekday_fig.clear()
        ax = self.weekday_fig.add_subplot(111)

        if weekdays and expenses:
            bars = ax.bar(weekdays, expenses, color="#ff6f61")
            ax.set_title("Средние расходы по дням недели")
            ax.set_ylabel("₽")
            ax.set_xlabel("День недели")
            ax.bar_label(bars, fmt="%.0f ₽", label_type="edge")
            ax.grid(True, linestyle="--", alpha=0.4)
            self.weekday_fig.tight_layout()
        else:
            ax.text(0.5, 0.5, "Нет данных для отображения", ha="center", va="center", fontsize=12, color="gray")

        self.weekday_canvas.draw()
        self.update_top_categories_chart()

    def update_top_categories_chart(self):
        categories, percentages = self.manager.get_top_expense_categories()
        if not categories:
            return

        self.top_fig.clear()
        ax = self.top_fig.add_subplot(111)
        ax.pie(percentages, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title("🏷️ Топ-5 категорий расходов")
