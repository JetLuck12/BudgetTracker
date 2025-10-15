from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QLabel, QPushButton, QLineEdit,
    QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt

from src.core.transaction import Transaction


class TransactionsTab(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Левая панель
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Категория")
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Заметка")

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_transaction)
        import_btn = QPushButton("📂 Импорт")
        import_btn.clicked.connect(self.import_report)
        delete_btn = QPushButton("🗑 Удалить")
        delete_btn.clicked.connect(self.delete_report)

        for w in [self.amount_input, self.category_input, self.note_input, add_btn, import_btn, delete_btn]:
            left_layout.addWidget(w)
        left_layout.addStretch(1)

        # Правая панель
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("🧾 История покупок"))
        self.transactions_list = QListWidget()
        right_layout.addWidget(self.transactions_list)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([300, 500])

        self.refresh_transactions()

    def add_transaction(self):
        try:

            amount = float(self.amount_input.text())
            self.manager.add_transaction(Transaction(amount = amount,
                                                     category = self.category_input.text().strip() or "Без категории",
                                                     note = self.note_input.text().strip(),
                                                     report_id=-1,
                                                     type_="Пополнение" if amount > 0 else "Списание"))
            self.amount_input.clear()
            self.category_input.clear()
            self.note_input.clear()
            QMessageBox.information(self, "Успешно", "Транзакция добавлена!")
            self.refresh_transactions()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму!")

    def import_report(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл отчёта", "", "Excel (*.xlsx *.xls);;CSV (*.csv)"
        )
        if not file_path:
            return
        try:
            report_id = self.manager.import_from_file(file_path)
            QMessageBox.information(self, "Импорт завершён", f"Отчёт импортирован (ID: {report_id})")
            self.refresh_transactions()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_report(self):
        report_id, ok = QInputDialog.getInt(self, "Удалить отчёт", "Введите ID отчёта:")
        if not ok:
            return
        try:
            self.manager.delete_report(report_id)
            QMessageBox.information(self, "Удалено", f"Отчёт #{report_id} удалён.")
            self.refresh_transactions()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def refresh_transactions(self):
        self.transactions_list.clear()
        transactions = self.manager.get_transactions()
        if type(transactions) != list:
            return
        for tran in transactions:
            sign = "+" if tran.type_ == "Пополнение" else "-"
            symbol = "🟩" if tran.type_ == "Пополнение" else "🟥"
            text = f"{symbol} {tran.date} | {sign}{tran.amount:.2f} ₽ | {tran.category}"
            if tran.note:
                text += f" — {tran.note}"
            text += f" | отчёт #{tran.report_id}"
            self.transactions_list.addItem(text)
