import datetime

def from_list(raw_trans):
    trans = list()
    for row in raw_trans:
        trans.append(Transaction(amount=row[1], category=row[2], note=row[3], date=row[0], report_id=row[4], type_=row[5]))


class Transaction:
    def __init__(self, amount, category, note, date=datetime.datetime.now(), report_id=0, type_="Списание"):
        self.amount : int = amount
        self.category : str= category
        self.note : str = note
        self.date : datetime.date = date
        self.report_id : int = report_id
        self.type_ : str = type_

    def __str__(self) -> str:
        return str(f"{self.report_id} - { "-" if self.type_ == "Списание" else "+"} {self.amount} - {self.category}: {self.note} ({self.date})")\

