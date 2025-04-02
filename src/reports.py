import os
import logging
from functools import wraps
from datetime import datetime
from typing import Optional

import pandas as pd
from src.utils import read_json


log_directory = "../logs"
os.makedirs(log_directory, exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(os.path.join(log_directory, "app.log"), mode='w', encoding='utf-8')


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)

def decorator_file(file_name):
    """
    Этот декоратор записывает результат выполнения функции в JSON файл. Принимает на вход имя файла или путь файла.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:

                logger.info(f"Выполнение функции: {func.__name__}")

                df = func(*args, **kwargs)

                if isinstance(df, pd.DataFrame):
                    df.to_json(file_name, orient="records", lines=True, force_ascii=False)
                    logger.info(f"Результат функции записан в файл: {file_name}")
                else:
                    return df

            except Exception as e:
                logger.error(f"Ошибка при выполнении функции {func.__name__}: {str(e)}")
                raise

        return inner

    return wrapper


@decorator_file("../data/report_decor.json")
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция принимает на вход датафрейм, категорию и дату. Возвращает JSON-файл с информацией о тратах в данной категории.
    """
    try:
        logger.info(f"Запрос для категории: {category} с датой: {date}")

        if not date:
            stop_date = datetime.now()
        else:

            stop_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
            stop_date = stop_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date = stop_date - pd.Timedelta(days=90)

        required_columns = ['Дата платежа', 'Категория', 'Сумма операции']


        if isinstance(transactions, list):
            transactions = pd.DataFrame(transactions)


        for column in required_columns:
            if column not in transactions.columns:
                logger.warning(f"Отсутствует обязательный столбец в данных: {column}")
                return pd.DataFrame()


        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors='coerce')


        filtered_transactions = transactions[
            (transactions["Дата платежа"] >= start_date) &
            (transactions["Дата платежа"] <= stop_date) &
            (transactions["Категория"] == category) &
            (transactions["Сумма операции"] < 0)
            ]


        if filtered_transactions.empty:
            logger.info(f"Нет данных для категории: {category} за выбранный период.")
            return pd.DataFrame({"Категория": [category], "Сумма трат": [0.0]})


        total_spending = round(filtered_transactions["Сумма операции"].abs().sum(), 2)


        result = pd.DataFrame({
            "Категория": [category],
            "Сумма трат": [total_spending]
        })

        logger.info(f"Результаты для категории '{category}': {total_spending} руб.")
        return result

    except ValueError as ve:
        logger.error(f"Ошибка ValueError: {str(ve)}")
        return pd.DataFrame({"Категория": [category], "Сумма трат": [0.0]})

    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {str(e)}")
        return pd.DataFrame({"Категория": [category], "Сумма трат": [0.0]})


# trans = read_json("../data/search_results.json")
# spending_by_category(trans, "Супермаркеты", "13.12.2020 23:59:59")
