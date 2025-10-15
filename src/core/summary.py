from enum import Enum

import pandas as pd

from .transaction import Transaction

class tran_type(Enum):
    Income = 0
    Outcome = 1
    All = 2

class Summary:
    @staticmethod
    def get_summary_by_category(transactions, tran_type_ = tran_type.All) -> dict[str, float]:
        summary = dict()
        for transaction in transactions:
            amount = 0
            if tran_type_ == tran_type.Income:
                amount = transaction.amount
            elif tran_type_ == tran_type.Outcome:
                amount = -transaction.amount
            elif tran_type_ == tran_type.All:
                amount = transaction.amount if transaction.type_ == "Пополнение" else -transaction.amount
            summary[transaction.category] += amount
        return summary

    @staticmethod
    def get_financial_summary(transactions) -> dict[str, float]:
        summary = dict()
        if type(transactions) != list:
            return summary
        for transaction in transactions:
            if transaction.type_ == "Списание":
                summary["expense"] += transaction.amount
            else:
                summary["income"] += transaction.amount

        summary["balance"] = summary["income"] - summary["expense"]
        summary["count"] = len(transactions)
        summary["avg_check"] = summary["income"] / summary["count"]
        return summary

    @staticmethod
    def get_graph_summary(transactions) -> list[list[float]]:
        summary = list()
        if type(transactions) != list:
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
        summary.append(balance.index.tolist())
        summary.append(balance.values.tolist())
        return summary

    @staticmethod
    def get_summary_by_weekday(transactions) -> dict[str, float]:
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
        df = df[df["type"] == "Списание"]
        if df.empty:
            return {}

        # Преобразуем дату в datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

        # Добавляем день недели (0 = понедельник, 6 = воскресенье)
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        df["weekday"] = df["date"].dt.dayofweek.apply(lambda i: weekdays[i] if pd.notna(i) else None)

        # Группировка по дням недели
        avg_expenses = df.groupby("weekday")["amount"].mean().reindex(weekdays)

        # Возвращаем как списки для построения графика
        return avg_expenses

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
        df = df[df["type"] == "Списание"]
        if df.empty:
            return {}

        category_sums = df.groupby("category")["amount"].sum().sort_values(ascending=False)

        total = category_sums.sum()
        percentages = (category_sums / total * 100).round(1)

        top_categories = percentages.head(top_n)

        return top_categories.to_dict()