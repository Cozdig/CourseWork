import json
import logging

import pandas as pd


def read_xlsx(input_file="../data/operations.xlsx"):
    """Функция принимает на вход путь до xlsx файла и возвращает список словарей."""
    try:
        df = pd.read_excel(input_file, engine="openpyxl")

        # Убираем строки, где нет номера карты
        df = df.dropna(subset=["Номер карты"])

        # Преобразуем DataFrame в список словарей
        data = df.to_dict(orient="records")

        logging.info(f"Successfully read the file: {input_file}, {len(data)} rows loaded.")
        return data
    except Exception as e:
        logging.error(f"Error reading xlsx file {input_file}: {e}")
        return []


# print(read_xlsx("../data/operations.xlsx"))


def read_json(file_path):
    """Функция принимает на вход путь до JSON файла и возвращает список словарей."""
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return []


def filter_by_date(date_str, input_file="../data/operations.xlsx", output_file="../data/filtered_operations.json"):
    """Функция принимает на вход дату в формате dd.mm.yyyy hh:mm:ss, путь до принимаемого файла,
    а также путь до выходящего файла, и возвращает отфильтрованный JSON файл. Фильтровка происходит от начала
    месяца заданной даты, до заданной даты."""
    df = pd.read_excel(input_file, engine="openpyxl")
    df.dropna(subset=["Номер карты"])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    target_date = pd.to_datetime(date_str, dayfirst=True, format="%d.%m.%Y %H:%M:%S")
    start_of_month = target_date.replace(day=1)
    filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= target_date)]
    sorted_filtered_df = filtered_df.sort_values(by=["Дата операции"])
    sorted_filtered_df["Дата операции"] = sorted_filtered_df["Дата операции"].dt.strftime("%d-%m-%Y %H:%M:%S")
    sorted_filtered_df.to_json(output_file, orient="records", force_ascii=False, indent=4)

    return output_file
