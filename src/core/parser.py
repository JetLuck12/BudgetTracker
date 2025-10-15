import pandas as pd
import os

class Parser:
    @staticmethod
    def parse_file(filename) -> pd.DataFrame:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filename, sep=None, engine='python')
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(filename)
        else:
            raise ValueError("Поддерживаются только файлы CSV или XLSX")
        return df