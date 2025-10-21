import os
from datetime import datetime
from .transaction import from_list, Transaction
from .summary import Summary, tran_type
from .parser import Parser
from .plan import PlanParser, Plan
from .DBManager import DBManager


class BudgetManager:
    def __init__(self):
        self.plan = None
        self.PLAN_FILE = "user_plan.json"
        self.DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "budget.db")
        self.undo_stack = []
        self.redo_stack = []
        self.dbmanager = DBManager(self.DB_FILE)
        self.is_undoing_redoing = False  # Флаг для предотвращения сохранения изменений во время отмены/повтора

    def add_transaction(self, tran : Transaction):
        transaction_id = self.dbmanager.add_transaction(tran)
        # Сохраняем действие в стек отмены
        self._save_to_undo_stack('add_transaction', transaction_id=transaction_id, transaction=tran)

    def delete_transaction(self, transaction_id: int):
        """Удаляет отдельную транзакцию с поддержкой отмены"""
        # Получаем транзакцию перед удалением
        transactions = self.get_transactions()
        transaction_to_delete = None
        for t in transactions:
            if t.id == transaction_id:
                transaction_to_delete = t
                break
        
        if transaction_to_delete is None:
            raise ValueError(f"Транзакция с ID {transaction_id} не найдена")
        
        # Удаляем транзакцию
        self.dbmanager.delete_transaction(transaction_id)
        # Сохраняем действие в стек отмены
        self._save_to_undo_stack('delete_transaction', transaction_id=transaction_id, transaction=transaction_to_delete)
        print(f"✅ Транзакция ID {transaction_id} удалена")

    def delete_report(self, report_id: int):
        # Получаем все транзакции отчёта перед удалением
        transactions = self.get_transactions()
        report_transactions = [t for t in transactions if t.report_id == report_id]
        
        self.dbmanager.delete_report(report_id)
        # Сохраняем действие в стек отмены
        self._save_to_undo_stack('delete_report', report_id=report_id, transactions=report_transactions)
        print(f"✅ Удалены все транзакции для отчёта ID {report_id}")

    def get_transactions(self) -> list[Transaction]:
        return self.dbmanager.get_transactions()

    def get_summary_by_category(self, tran_type_ = tran_type.All) -> dict[str, float]:
        transactions = self.get_transactions()
        return Summary.get_summary_by_category(transactions, tran_type_)

    def get_financial_summary(self) -> dict[str, float]:
        transactions = self.get_transactions()
        return Summary.get_financial_summary(transactions)

    def get_next_report_id(self, filename) -> int:
        return self.dbmanager.get_next_report_id(filename)

    def import_from_file(self, filepath) -> int:
        """
        Импортирует покупки из .CSV или .XLSX файла
        """
        df = Parser.parse_file(filepath)

        expected_cols = ["Дата операции", "Номер счета", "Описание операции", "Сумма", "Категория", "Тип", "Комментарий", "Кэшбэк"]
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Не найдены столбцы: {', '.join(missing)}")

        report_id = self.get_next_report_id(filepath)

        for _, row in df.iterrows():
            try:
                amount = float(row["Сумма"])
            except ValueError:
                continue
            transaction = Transaction(amount = amount,
                                      report_id = report_id,
                                      category = str(row["Категория"]),
                                      note = f"{row['Описание операции']} ({row['Комментарий']})",
                                      date = str(row["Дата операции"]),
                                      type_ = str(row["Тип"]))
            self.add_transaction(transaction)
        print(f"✅ Импорт завершён. Добавлено {len(df)} операций в отчёт #{report_id}")
        return report_id

    def get_graph_summary(self) -> list[list[float]]:
        """Возвращает список точек (date, cumulative_balance)"""
        transactions = self.get_transactions()

        return Summary.get_graph_summary(transactions)

    def get_expenses_by_weekday(self) -> dict[str, float]:
        """
        Возвращает средние траты по дням недели.
        Использует поле 'date' и 'type' ('Списание' или 'Пополнение').
        """
        transactions = self.get_transactions()
        return Summary.get_summary_by_weekday(transactions)

    def get_top_expense_categories(self, top_n=5) -> dict[str, float]:
        """
        Возвращает топ-N категорий расходов с процентами.
        """
        transactions = self.get_transactions()
        return Summary.get_top_expenses(transactions, top_n)

    def save_plan(self, plan):
        PlanParser.save_plan(plan, self.PLAN_FILE)

    def load_plan(self):
        raw_plan  = PlanParser.parse(self.PLAN_FILE)
        self.plan = Plan(raw_plan)

    def save_plan_changes(self, old_plan_state, new_plan_state):
        """Сохраняет изменения плана в стек отмены"""
        if not self.is_undoing_redoing:  # Сохраняем только если не выполняем отмену/повтор
            self._save_to_undo_stack('update_plan', old_state=old_plan_state, new_state=new_plan_state)

    def get_current_plan_state(self):
        """Возвращает текущее состояние плана в виде словаря"""
        if not self.plan:
            return {}
        return self.plan.plan.copy()

    def apply_plan_state(self, plan_state):
        """Применяет состояние плана"""
        if self.plan:
            self.plan.plan = plan_state.copy()
        else:
            # Создаем новый план с данными
            plan_json = []
            for category, amount in plan_state.items():
                plan_json.append({
                    "category": category,
                    "plan_expense": amount
                })
            self.plan = Plan(plan_json)
        # Сохраняем в файл
        self.save_plan(self.plan)

    def get_all_categories(self) -> list[str]:
        return self.dbmanager.get_categories()

    def get_income_for_category(self, category: str) -> float:
        return self.dbmanager.get_income_for_category(category)

    def get_expense_for_category(self, category: str) -> float:
        return self.dbmanager.get_expense_for_category(category)

    def get_income_categories(self) -> list[str]:
        """Возвращает список категорий, которые имеют доходы (пополнения)"""
        transactions = self.get_transactions()
        income_categories = set()
        for transaction in transactions:
            if transaction.type_ == "Пополнение":
                income_categories.add(transaction.category)
        return sorted(income_categories)

    def get_expense_categories(self) -> list[str]:
        """Возвращает список категорий, которые имеют расходы (списания)"""
        transactions = self.get_transactions()
        expense_categories = set()
        for transaction in transactions:
            if transaction.type_ == "Списание":
                expense_categories.add(transaction.category)
        return sorted(expense_categories)

    def undo(self):
        """Отменяет последнее действие"""
        if not self.undo_stack:
            return False
        
        self.is_undoing_redoing = True  # Устанавливаем флаг
        last_action = self.undo_stack.pop()
        self.redo_stack.append(last_action)
        
        if last_action['type'] == 'add_transaction':
            # Удаляем транзакцию
            self.dbmanager.delete_transaction(last_action['transaction_id'])
        elif last_action['type'] == 'delete_transaction':
            # Восстанавливаем транзакцию
            transaction = last_action['transaction']
            self.dbmanager.add_transaction(transaction)
            print(f"✅ Транзакция ID {transaction.id} восстановлена")
        elif last_action['type'] == 'delete_report':
            # Восстанавливаем все транзакции отчёта
            for transaction in last_action['transactions']:
                self.dbmanager.add_transaction(transaction)
        elif last_action['type'] == 'update_plan':
            # Восстанавливаем предыдущее состояние плана
            old_state = last_action['old_state']
            self.apply_plan_state(old_state)
        
        return True

    def redo(self):
        """Повторяет отменённое действие"""
        if not self.redo_stack:
            return False
        
        self.is_undoing_redoing = True  # Устанавливаем флаг
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        
        if action['type'] == 'add_transaction':
            # Добавляем транзакцию обратно
            transaction = action['transaction']
            self.dbmanager.add_transaction(transaction)
        elif action['type'] == 'delete_transaction':
            # Удаляем транзакцию
            self.dbmanager.delete_transaction(action['transaction_id'])
            print(f"✅ Транзакция ID {action['transaction_id']} удалена повторно")
        elif action['type'] == 'delete_report':
            # Удаляем все транзакции отчёта
            self.dbmanager.delete_report(action['report_id'])
        elif action['type'] == 'update_plan':
            # Применяем новое состояние плана
            new_state = action['new_state']
            self.apply_plan_state(new_state)
        
        return True

    def _save_to_undo_stack(self, action_type, **kwargs):
        """Сохраняет действие в стек отмены"""
        action = {'type': action_type, **kwargs}
        self.undo_stack.append(action)
        # Очищаем стек повтора при новом действии
        self.redo_stack.clear()