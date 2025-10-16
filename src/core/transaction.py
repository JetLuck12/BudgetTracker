import datetime

def from_list(raw_trans):
    trans = []
    for row in raw_trans:
        trans.append(Transaction(id_=row[0], amount=row[2], category=row[3], note=row[4], date=row[1], report_id=row[5], type_=row[6]))
    return trans


class Transaction:
    def __init__(self, amount, category, note, date=datetime.datetime.now(), report_id=0, type_="Списание", id_=None):
        self.id = id_
        self.amount : int = amount
        self.category : str= category
        self.note : str = note
        self.date : datetime.date = date
        self.report_id : int = report_id
        self.type_ : str = type_

    def __str__(self) -> str:
        return str(f"{self.report_id} - { "-" if self.type_ == "Списание" else "+"} {self.amount} - {self.category}: {self.note} ({self.date})")\

