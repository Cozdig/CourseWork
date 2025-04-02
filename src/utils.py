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

def read_json(file_path):
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    return data


def filter_by_date(date_str, input_file="../data/operations.xlsx", output_file="../data/filtered_operations.json"):
    df = pd.read_excel(input_file, engine="openpyxl")
    df.dropna(subset=["Номер карты"])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    target_date = pd.to_datetime(date_str, dayfirst=True, format="%d.%m.%Y %H:%M:%S")
    start_of_month = target_date.replace(day=1)
    filtered_df = df[
        (df["Дата операции"] >= start_of_month) &
        (df["Дата операции"] <= target_date)
        ]
    sorted_filtered_df = filtered_df.sort_values(by=["Дата операции"])
    sorted_filtered_df["Дата операции"] = sorted_filtered_df["Дата операции"].dt.strftime("%d-%m-%Y %H:%M:%S")
    sorted_filtered_df.to_json(
        output_file,
        orient="records",
        force_ascii=False,
        indent=4
    )

    return output_file