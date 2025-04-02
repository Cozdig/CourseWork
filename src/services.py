import json
import logging
import re

import pandas as pd

from src.utils import read_xlsx

logging.basicConfig(
    filename="../logs/search.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
    encoding="utf-8",
    force=True
)

def re_sort(way, search, output_file="../data/search_results.json"):
    """Читает xlsx, ищет совпадения и записывает результат в JSON-файл."""
    logging.info(f"Начало работы re_sort: путь={way}, поиск={search}")

    try:
        df = read_xlsx(way)

        # Если df это список, преобразуем его в DataFrame
        if isinstance(df, list):
            df = pd.DataFrame(df)

        if df is None or df.empty:
            logging.warning(f"Файл {way} пуст или не загружен.")
            result = []
        else:
            if not isinstance(df, pd.DataFrame):
                logging.error(f"Ошибка: read_xlsx вернул {type(df)}, а ожидался DataFrame.")
                raise ValueError("Функция read_xlsx должна возвращать DataFrame")

            # Заменяем NaN на 0, чтобы в JSON было 0
            df = df.fillna(0)

            list_transactions = df.to_dict(orient="records")
            pattern = re.compile(search, re.IGNORECASE)

            result = [
                operation
                for operation in list_transactions
                if pattern.search(str(operation.get("Категория", ""))) or
                   pattern.search(str(operation.get("Описание", "")))
            ]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        logging.info(f"Результат ({len(result)} совпадений) записан в {output_file}.")

    except Exception as e:
        logging.error(f"Ошибка в re_sort: {str(e)}", exc_info=True)
        result = {"error": "Ошибка обработки файла"}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    return output_file

re_sort("../data/operations.xlsx", "Магнит")