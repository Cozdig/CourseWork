import pandas as pd
import json


def transactions_excel(file):
    """Читает Excel-файл и возвращает список транзакций."""
    try:
        df = pd.read_excel(file, engine="openpyxl")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return "Файл не найден"
    except Exception as e:
        return f"Ошибка: {e}"

print(transactions_excel("../data/operations.xlsx"))

def read_json(file_path):
    """Читает данные из JSON-файла и возвращает их как Python объект (например, список или словарь)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Файл по пути {file_path} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")