from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.core.summary import tran_type


class PlanTab(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.current_plan_state = {}  # Текущее состояние плана
        self.init_ui()
        self.load_existing_plan()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        title = QLabel("📅 Финансовый план")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # --- Контейнер для двух таблиц рядом ---
        tables_layout = QHBoxLayout()
        main_layout.addLayout(tables_layout)

        # Таблица пополнений (доходов)
        self.income_table = QTableWidget()
        self.income_table.setColumnCount(4)
        self.income_table.setHorizontalHeaderLabels(["Категория", "План", "Факт", "Разница"])
        self.income_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.income_table.itemChanged.connect(self.update_income_diff)
        # Таблица расходов (списаний)
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)
        self.expense_table.setHorizontalHeaderLabels(["Категория", "План", "Факт", "Разница"])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


        self.expense_table.itemChanged.connect(self.update_expense_diff)

        # Добавляем таблицы в горизонтальный блок
        tables_layout.addWidget(self.income_table)
        tables_layout.addWidget(self.expense_table)

        # Кнопка обновления
        save_btn = QPushButton("💾 Пересчитать")
        save_btn.clicked.connect(self.recalculate_difference)
        main_layout.addWidget(save_btn)

        self.result_label = QLabel()
        main_layout.addWidget(self.result_label)

    def load_existing_plan(self):
        # Получаем категории по типу транзакций
        income_cats = self.manager.get_income_categories()
        expense_cats = self.manager.get_expense_categories()

        if not income_cats and not expense_cats:
            return
        
        # Сохраняем текущее состояние плана
        self.current_plan_state = self.manager.get_current_plan_state()

        # --- доходы (пополнения) ---
        self.income_table.setRowCount(len(income_cats))
        for row, cat in enumerate(income_cats):
            actual_income = self.manager.get_income_for_category(cat)
            planned_income = self.current_plan_state.get(cat, 0)
            diff = actual_income - planned_income

            self.income_table.setItem(row, 0, QTableWidgetItem(cat))
            self.income_table.setItem(row, 1, QTableWidgetItem(f"{planned_income:.2f}"))
            self.income_table.setItem(row, 2, QTableWidgetItem(f"{actual_income:.2f}"))
            self.income_table.setItem(row, 3, QTableWidgetItem(f"{diff:+.2f}"))

            # Делаем категорию и факт нередактируемыми
            for col in [0, 2, 3]:
                item = self.income_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # --- расходы (списания) ---
        self.expense_table.setRowCount(len(expense_cats))
        for row, cat in enumerate(expense_cats):
            actual_expense = self.manager.get_expense_for_category(cat)
            planned_expense = self.current_plan_state.get(cat, 0)
            diff = planned_expense - actual_expense  # экономия положительная

            self.expense_table.setItem(row, 0, QTableWidgetItem(cat))
            self.expense_table.setItem(row, 1, QTableWidgetItem(f"{planned_expense:.2f}"))
            self.expense_table.setItem(row, 2, QTableWidgetItem(f"{actual_expense:.2f}"))
            self.expense_table.setItem(row, 3, QTableWidgetItem(f"{diff:+.2f}"))

            for col in [0, 2, 3]:
                item = self.expense_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def recalculate_difference(self):
        income_diff = 0
        expense_diff = 0

        # --- Доходы ---
        for row in range(self.income_table.rowCount()):
            planned = float(self.income_table.item(row, 1).text() or 0)
            actual = float(self.income_table.item(row, 2).text() or 0)
            income_diff += actual - planned

        # --- Расходы ---
        for row in range(self.expense_table.rowCount()):
            planned = float(self.expense_table.item(row, 1).text() or 0)
            actual = float(self.expense_table.item(row, 2).text() or 0)
            expense_diff += planned - actual  # экономия положительная

        total_diff = income_diff + expense_diff

        self.result_label.setText(
            f"📊 Итог: доходы {income_diff:+.2f} ₽, "
            f"экономия по расходам {expense_diff:+.2f} ₽, "
            f"баланс изменения {total_diff:+.2f} ₽"
        )

    def update_income_diff(self, item):
        row = item.row()
        col = item.column()

        # Пересчитываем только если изменили колонку "План" (1)
        if col == 1:
            try:
                planned = float(self.income_table.item(row, 1).text())
                actual_item = self.income_table.item(row, 2)
                if actual_item is None:
                    actual_value = 0.0
                else:
                    try:
                        actual_value = float(actual_item.text())
                    except ValueError:
                        actual_value = 0.0
                diff = actual_value - planned
                diff_item = QTableWidgetItem(f"{diff:+.2f}")

                self.income_table.blockSignals(True)
                self.income_table.setItem(row, 3, diff_item)
                self.income_table.blockSignals(False)

                # Можно добавить цветовую подсветку
                if diff < 0:
                    diff_item.setBackground(Qt.GlobalColor.red)
                else:
                    diff_item.setBackground(Qt.GlobalColor.green)
                
                # Сохраняем изменение в стек отмены
                self.save_plan_change()
            except ValueError:
                pass  # если не число, игнорируем

    def update_expense_diff(self, item):
        row = item.row()
        col = item.column()

        if col == 1:  # только если изменили план
            try:
                planned = float(self.expense_table.item(row, 1).text())
                actual_item = self.expense_table.item(row, 2)
                if actual_item is None:
                    actual_value = 0.0
                else:
                    try:
                        actual_value = float(actual_item.text())
                    except ValueError:
                        actual_value = 0.0

                diff = planned - actual_value  # экономия
                diff_item = QTableWidgetItem(f"{diff:+.2f}")

                self.expense_table.blockSignals(True)
                self.expense_table.setItem(row, 3, diff_item)
                self.expense_table.blockSignals(False)

                # Цвет подсветки
                if diff < 0:
                    diff_item.setBackground(Qt.GlobalColor.red)
                else:
                    diff_item.setBackground(Qt.GlobalColor.green)
                
                # Сохраняем изменение в стек отмены
                self.save_plan_change()
            except ValueError:
                pass

    def refresh_plan(self):
        """Обновляет план после изменений в транзакциях"""
        self.load_existing_plan()
        self.recalculate_difference()

    def save_plan_change(self):
        """Сохраняет изменение плана в стек отмены"""
        # Получаем новое состояние плана из таблиц
        new_plan_state = {}
        
        # Собираем данные из таблицы доходов
        for row in range(self.income_table.rowCount()):
            category_item = self.income_table.item(row, 0)
            plan_item = self.income_table.item(row, 1)
            if category_item and plan_item:
                try:
                    category = category_item.text()
                    amount = float(plan_item.text())
                    new_plan_state[category] = amount
                except ValueError:
                    pass
        
        # Собираем данные из таблицы расходов
        for row in range(self.expense_table.rowCount()):
            category_item = self.expense_table.item(row, 0)
            plan_item = self.expense_table.item(row, 1)
            if category_item and plan_item:
                try:
                    category = category_item.text()
                    amount = float(plan_item.text())
                    new_plan_state[category] = amount
                except ValueError:
                    pass
        
        # Сохраняем изменение только если состояние действительно изменилось
        if new_plan_state != self.current_plan_state:
            # Проверяем, не выполняется ли сейчас отмена/повтор
            if not self.manager.is_undoing_redoing:
                self.manager.save_plan_changes(self.current_plan_state, new_plan_state)
            self.current_plan_state = new_plan_state.copy()
            
            # Сохраняем план в файл
            self.save_plan_to_file(new_plan_state)

    def save_plan_to_file(self, plan_state):
        """Сохраняет план в файл"""
        try:
            # Создаем JSON структуру для плана
            plan_json = []
            for category, amount in plan_state.items():
                plan_json.append({
                    "category": category,
                    "plan_expense": amount
                })
            
            # Сохраняем через менеджер
            if self.manager.plan:
                self.manager.plan.plan = plan_state.copy()
            else:
                # Создаем новый план
                from src.core.plan import Plan
                self.manager.plan = Plan(plan_json)
            
            self.manager.save_plan(self.manager.plan)
            print("💾 План сохранён в файл")
        except Exception as e:
            print(f"❌ Ошибка сохранения плана: {e}")