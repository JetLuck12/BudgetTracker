import sqlite3
import os
from datetime import datetime

from src.core.transaction import Transaction, from_list


class DBManager:
    def __init__(self, db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS reports (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    filename TEXT,
                                    import_date TEXT
                                )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    report_id INTEGER,
                                    amount REAL,
                                    category TEXT,
                                    note TEXT,
                                    date TEXT,
                                    type TEXT,
                                    FOREIGN KEY (report_id) REFERENCES reports(id)
                                )''')

    def get_categories(self) -> list[str]:
        """Возвращает список уникальных категорий из базы"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM transactions")
        rows = cursor.fetchall()
        return [r[0] for r in rows if r[0]]

    def get_income_for_category(self, category: str) -> float:
        """Возвращает сумму доходов ('Пополнение') по указанной категории"""
        cursor = self.conn.cursor()
        cursor.execute("""
                    SELECT SUM(amount)
                    FROM transactions
                    WHERE category = ? AND type = 'Пополнение'
                """, (category,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0

    def get_expense_for_category(self, category: str) -> float:
        """Возвращает сумму расходов ('Списание') по указанной категории"""
        cursor = self.conn.cursor()
        cursor.execute("""
                    SELECT SUM(amount)
                    FROM transactions
                    WHERE category = ? AND type = 'Списание'
                """, (category,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0

    def add_transaction(self, tran: Transaction):
        if tran.report_id == -1:
            tran.report_id = self.get_next_report_id("User addition")
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (report_id, amount, category, note, date, type) VALUES (?, ?, ?, ?, ?, ?)",
            (tran.report_id, tran.amount, tran.category, tran.note, tran.date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tran.type_)
        )
        self.conn.commit()

    def delete_report(self, report_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE report_id = ?", (report_id,))
        self.conn.commit()

    def get_transactions(self) -> list[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, amount, category, note, report_id, type FROM transactions ORDER BY date DESC")
        raw_trans = cursor.fetchall()
        return from_list(raw_trans)

    def get_next_report_id(self, filename) -> int:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO reports (filename, import_date) VALUES (?, ?)",
                       (os.path.basename(filename), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return cursor.lastrowid
