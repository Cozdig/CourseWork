import datetime
import json
import logging
import os

import requests
from dotenv import load_dotenv

from src.utils import filter_by_date, read_json

# Настройка логирования
log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "views.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file, "w", encoding="utf-8"), logging.StreamHandler()],
)

load_dotenv()
api_key = os.getenv("CURRENCY_API_KEY")
api_key_sp = os.getenv("500_API_KEY")

try:
    with open("../user_settings.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    tickers = data.get("user_stocks", [])
    user_currencies = data.get("user_currencies", [])
    logging.info("Successfully loaded user settings.")
except Exception as e:
    logging.error(f"Error loading user settings: {e}")
    tickers, user_currencies = [], []


def log_error(func):
    """Декоратор для логирования ошибок"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return None

    return wrapper


@log_error
def sp_tracker():
    """Функция отслеживает акции и возвращает цены акций."""
    base_url = "https://www.alphavantage.co/query"
    stock_prices = []
    for ticker in tickers:
        params = {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": api_key_sp}
        response = requests.get(base_url, params=params)
        logging.info(f"Request for ticker {ticker}: {response.url}")
        data = response.json()
        if "Global Quote" in data:
            price = data["Global Quote"].get("05. price", "0")
            stock_prices.append({"stock": ticker, "price": convert_currency(price, "USD", "RUB")})
        else:
            stock_prices.append({"stock": ticker, "price": f"Ошибка получения данных для {ticker}"})
            logging.error(f"Error getting data for {ticker}")
    return stock_prices


@log_error
def convert_currency(amount, from_currency, to_currency):
    """Функция берет кол-во денег, валюту из которой переводят и валюту в которую переводят,
    и возвращает деньги в заданной валюте в 3 аргументе."""
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        exchange_rate = data["conversion_rates"].get(to_currency)
        if exchange_rate:
            return round(float(amount) * exchange_rate, 2)
        return "Currency not supported"
    logging.error(f"Currency conversion error: {data.get('error', {}).get('info', 'Unknown error')}")
    return "Conversion failed"


@log_error
def day_time():
    """Эта функция считывает время суток и возвращает сообщение для пользователя"""
    hour = datetime.datetime.now().hour
    if 3 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


@log_error
def cards(operation_info):
    """Функция считывает список словарей из таблицы, и возвращает кол-во потраченных денег на карте."""
    if not operation_info:
        logging.error("No operation info provided to cards function.")
        return {}

    unique_cards = {}
    try:
        for operation in operation_info:
            card_number = operation.get("Номер карты")
            if card_number:
                card_number = card_number[-4:]
            summa = summ(operation)

            if card_number in unique_cards:
                unique_cards[card_number]["sum"] += summa
            else:
                unique_cards[card_number] = {"sum": summa}
    except Exception as e:
        logging.error(f"Error in cards: {e}")
    return unique_cards


@log_error
def summ(operation_info):
    """Функция берет все суммы операций из таблицы, округляет их и возвращает."""
    return round(float(operation_info.get("Сумма операции с округлением", 0)), 2)


@log_error
def cashback(operation_info):
    """Функция считает кол-во кешбека, накопленного за операции, которые подаются на вход функции."""
    return [
        {"card_number": card, "sum": data["sum"], "cashback": round(data["sum"] * 0.01, 2)}
        for card, data in cards(operation_info).items()
    ]


@log_error
def top_5_transactions(operation_info):
    """Функция принимает на вход данные из таблицы и возвращает топ 5 самых больших транзакций."""
    return sorted(
        [
            {
                "date": op.get("Дата операции"),
                "amount": op.get("Сумма платежа"),
                "category": op.get("Категория"),
                "description": op.get("Описание"),
            }
            for op in operation_info
        ],
        key=lambda x: x["amount"],
        reverse=True,
    )[:5]


@log_error
def currency_course(operation_info):
    """Функция считывает транзакции с иностранными валютами и возвращает их, уже переведенные в рубль."""
    return convert_currency(operation_info.get("Сумма операции"), operation_info.get("Валюта операции"), "RUB")


@log_error
def main_views(date):
    """Основная функция, которая собирает все функции выше. Она принимает на вход дату в формате
    dd.mm.yyyy hh:mm:ss и возвращает JSON файл с данными о транзакциях, а также курс валют и стоимость акций."""
    file_name = filter_by_date(date)
    if not file_name:
        logging.error("No valid file name found for the given date.")
        return

    operations = read_json("../data/filtered_operations.json")
    if not operations:
        logging.error("Failed to load operations from JSON.")
        return

    logging.info(f"Loaded operations: {operations}")
    output = {
        "greeting": day_time(),
        "cards": [
            {"last_digits": card, "total_spent": round(data["sum"], 2), "cashback": round(data["sum"] * 0.01, 2)}
            for card, data in cards(operations).items()
            if type(card) == str
        ],
        "top_transactions": top_5_transactions(operations),
        "currency_rates": [{"currency": curr, "rate": convert_currency(1, curr, "RUB")} for curr in user_currencies],
        "stock_prices": sp_tracker(),
    }
    report_file_path = "../data/report.json"
    with open(report_file_path, "w", encoding="utf-8") as report_file:
        json.dump(output, report_file, indent=2, ensure_ascii=False)
    logging.info(f"Report saved successfully to {report_file_path}")


# date_string = "20.11.2021 23:11:24"
# main_views(date_string)
