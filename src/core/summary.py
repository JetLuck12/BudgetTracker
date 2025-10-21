from collections import defaultdict
from email.policy import default
from enum import Enum

import pandas as pd

from .transaction import Transaction

class tran_type(Enum):
    Income = 0
    Outcome = 1
    All = 2

# Константы
EXPENSE_TYPE = "Списание"
INCOME_TYPE = "Пополнение"

class Summary:
    @staticmethod
    def get_summary_by_category(transactions, tran_type_ = tran_type.All) -> dict[str, float]:
        summary = defaultdict(float)
        for transaction in transactions:
            amount = 0
            if tran_type_ == tran_type.Income:
                if transaction.type_ == INCOME_TYPE:
                    amount = transaction.amount
            elif tran_type_ == tran_type.Outcome:
                if transaction.type_ == EXPENSE_TYPE:
                    amount = -transaction.amount
            elif tran_type_ == tran_type.All:
                amount = transaction.amount if transaction.type_ == INCOME_TYPE else -transaction.amount
            summary[transaction.category] += amount
        return summary

    @staticmethod
    def get_financial_summary(transactions) -> dict[str, float]:
        summary = {}
        summary["expense"] = 0
        summary["income"] = 0
        summary["balance"] = 0
        summary["count"] = 0
        summary["avg_check"] = 0.0
        
        if not isinstance(transactions, list):
            return summary
            
        for transaction in transactions:
            if transaction.type_ == EXPENSE_TYPE:
                summary["expense"] += transaction.amount
            else:
                summary["income"] += transaction.amount

        summary["balance"] = summary["income"] - summary["expense"]
        summary["count"] = len(transactions)
        summary["avg_check"] = summary["income"] / summary["count"] if summary["count"] > 0 else 0.0
        return summary

    @staticmethod
    def get_graph_summary(transactions) -> list[list[float]]:
        summary = []
        if not isinstance(transactions, list):
            return summary
        df = pd.DataFrame([{
            "date": t.date,
            "amount": t.amount,
            "category": t.category,
            "note": t.note,
            "report_id": t.report_id,
            "type": t.type_
        } for t in transactions])

        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
        df = df.sort_values("date")

        df["signed_amount"] = df.apply(
            lambda r: r["amount"] if r["type"] == "Пополнение" else -r["amount"],
            axis=1
        )

        balance = df.groupby("date")["signed_amount"].sum().cumsum()
        # Преобразуем даты в числовые значения (timestamp)
        dates_as_numbers = [int(date.timestamp()) for date in balance.index]
        summary.append(dates_as_numbers)
        summary.append(balance.values.tolist())
        return summary

    @staticmethod
    def get_summary_by_weekday(transactions):
        # Преобразуем в DataFrame для удобства анализа
        df = pd.DataFrame([{
            "date": t.date,
            "amount": t.amount,
            "category": t.category,
            "note": t.note,
            "report_id": t.report_id,
            "type": t.type_
        } for t in transactions])

        # Фильтруем только расходы
        df = df[df["type"] == EXPENSE_TYPE]
        if df.empty:
            return {}

        # Преобразуем дату в datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

        # Добавляем день недели (0 = понедельник, 6 = воскресенье)
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        df["weekday"] = df["date"].dt.dayofweek.apply(lambda i: weekdays[i] if pd.notna(i) else None)

        # Группировка по дням недели
        avg_expenses = df.groupby("weekday")["amount"].mean().reindex(weekdays)

        # Возвращаем как словарь
        return avg_expenses.to_dict()

    @staticmethod
    def get_top_expenses(transactions, top_n=5) -> dict[str, float]:
        df = pd.DataFrame([{
            "date": t.date,
            "amount": t.amount,
            "category": t.category,
            "note": t.note,
            "report_id": t.report_id,
            "type": t.type_
        } for t in transactions])
        df = df[df["type"] == EXPENSE_TYPE]
        if df.empty:
            return {}

        category_sums = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        total = category_sums.sum()
        percentages = (category_sums / total * 100).round(1)

        top_categories = percentages.head(top_n)
        return top_categories.to_dict()