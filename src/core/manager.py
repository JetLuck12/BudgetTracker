from datetime import datetime
from .transaction import from_list
from .summary import *
from .parser import *
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

    def add_transaction(self, tran : Transaction):
        self.dbmanager.add_transaction(tran)

    def delete_report(self, report_id: int):
        self.dbmanager.delete_report(report_id)
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