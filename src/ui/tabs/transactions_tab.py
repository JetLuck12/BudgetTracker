from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QLabel, QPushButton, QLineEdit,
    QMessageBox, QFileDialog, QInputDialog, QScrollArea,
    QCheckBox, QDialog
)
from PyQt6.QtCore import Qt
import json
import os

from src.core.transaction import Transaction

# Константы
INCOME_TYPE = "Пополнение"
ERROR_TITLE = "Ошибка"
PREFS_FILE = "user_preferences.json"


class CustomMessageBox(QDialog):
    """Кастомный MessageBox с чекбоксом 'Больше не показывать'"""
    
    def __init__(self, title, message, message_type="info", parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.message_type = message_type
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.resize(400, 150)
        
        layout = QVBoxLayout(self)
        
        # Сообщение
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Чекбокс
        self.dont_show_checkbox = QCheckBox("Больше не показывать это сообщение")
        layout.addWidget(self.dont_show_checkbox)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
    def should_show_message(self):
        """Проверяет, нужно ли показывать сообщение"""
        prefs = self.load_preferences()
        key = f"dont_show_{self.message_type}_{self.title.lower().replace(' ', '_')}"
        return not prefs.get(key, False)
    
    def save_preference(self):
        """Сохраняет настройку пользователя"""
        if self.dont_show_checkbox.isChecked():
            prefs = self.load_preferences()
            key = f"dont_show_{self.message_type}_{self.title.lower().replace(' ', '_')}"
            prefs[key] = True
            self.save_preferences(prefs)
    
    def load_preferences(self):
        """Загружает настройки пользователя"""
        try:
            if os.path.exists(PREFS_FILE):
                with open(PREFS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_preferences(self, prefs):
        """Сохраняет настройки пользователя"""
        try:
            with open(PREFS_FILE, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def show_message(self):
        """Показывает сообщение, если пользователь не отключил его"""
        if self.should_show_message():
            self.exec()
            self.save_preference()


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
        reset_notifications_btn = QPushButton("🔔 Сбросить уведомления")
        reset_notifications_btn.clicked.connect(self.reset_notification_preferences)

        for w in [self.amount_input, self.category_input, self.note_input, add_btn, import_btn, delete_btn, reset_notifications_btn]:
            left_layout.addWidget(w)
        left_layout.addStretch(1)

        # Правая панель
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("🧾 История покупок"))
        
        # Создаем область прокрутки для транзакций
        scroll_area = QScrollArea()
        self.transactions_widget = QWidget()
        self.transactions_layout = QVBoxLayout(self.transactions_widget)
        scroll_area.setWidget(self.transactions_widget)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

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
                                                     type_=INCOME_TYPE if amount > 0 else "Списание"))
            self.amount_input.clear()
            self.category_input.clear()
            self.note_input.clear()
            CustomMessageBox("Успешно", "Транзакция добавлена!", "success", self).show_message()
            self.refresh_transactions()
        except ValueError:
            CustomMessageBox(ERROR_TITLE, "Введите корректную сумму!", "warning", self).show_message()

    def import_report(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл отчёта", "", "Excel (*.xlsx *.xls);;CSV (*.csv)"
        )
        if not file_path:
            return
        try:
            report_id = self.manager.import_from_file(file_path)
            CustomMessageBox("Импорт завершён", f"Отчёт импортирован (ID: {report_id})", "success", self).show_message()
            self.refresh_transactions()
        except Exception as e:
            CustomMessageBox(ERROR_TITLE, str(e), "error", self).show_message()

    def delete_report(self):
        report_id, ok = QInputDialog.getInt(self, "Удалить отчёт", "Введите ID отчёта:")
        if not ok:
            return
        try:
            self.manager.delete_report(report_id)
            CustomMessageBox("Удалено", f"Отчёт #{report_id} удалён.", "success", self).show_message()
            self.refresh_transactions()
        except Exception as e:
            CustomMessageBox(ERROR_TITLE, str(e), "error", self).show_message()

    def refresh_transactions(self):
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.transactions_layout.count())):
            item = self.transactions_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        transactions = self.manager.get_transactions()
        if not isinstance(transactions, list):
            return
        
        for tran in transactions:
            transaction_widget = self.create_transaction_widget(tran)
            self.transactions_layout.addWidget(transaction_widget)
        
        # Добавляем растягивающий элемент в конец
        self.transactions_layout.addStretch()

    def create_transaction_widget(self, transaction):
        """Создает виджет для отображения одной транзакции с кнопкой удаления"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Формируем текст транзакции
        sign = "+" if transaction.type_ == INCOME_TYPE else "-"
        symbol = "🟩" if transaction.type_ == INCOME_TYPE else "🟥"
        text = f"{symbol} {transaction.date} | {sign}{transaction.amount:.2f} ₽ | {transaction.category}"
        if transaction.note:
            text += f" — {transaction.note}"
        text += f" | отчёт #{transaction.report_id}"
        
        # Создаем лейбл с информацией о транзакции
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label, 1)
        
        # Создаем кнопку удаления
        delete_btn = QPushButton("🗑")
        delete_btn.setMaximumWidth(30)
        delete_btn.setToolTip("Удалить транзакцию")
        delete_btn.clicked.connect(lambda: self.delete_transaction(transaction.id))
        layout.addWidget(delete_btn)
        
        return widget

    def delete_transaction(self, transaction_id):
        """Удаляет транзакцию по её ID с поддержкой отмены"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение удаления", 
            "Вы уверены, что хотите удалить эту транзакцию?\n\n💡 Вы сможете отменить это действие с помощью Ctrl+Z",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_transaction(transaction_id)
                CustomMessageBox("Успешно", "Транзакция удалена!\n\n💡 Используйте Ctrl+Z для отмены", "success", self).show_message()
                self.refresh_transactions()
            except Exception as e:
                CustomMessageBox(ERROR_TITLE, f"Не удалось удалить транзакцию: {str(e)}", "error", self).show_message()
    
    def reset_notification_preferences(self):
        """Сбрасывает все настройки уведомлений"""
        try:
            if os.path.exists(PREFS_FILE):
                os.remove(PREFS_FILE)
            CustomMessageBox("Настройки сброшены", "Все настройки уведомлений сброшены. Уведомления снова будут показываться.", "info", self).show_message()
        except Exception as e:
            CustomMessageBox(ERROR_TITLE, f"Не удалось сбросить настройки: {str(e)}", "error", self).show_message()
