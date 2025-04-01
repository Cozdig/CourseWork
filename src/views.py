import os
import datetime
from dotenv import load_dotenv
import requests
import json
import pandas as pd
from src.utils import read_json


load_dotenv()
api_key = os.getenv("CURRENCY_API_KEY")
api_key_sp = os.getenv("500_API_KEY")

with open("../user_settings.json", "r", encoding="utf-8") as file:
    tickers = json.load(file)

tickers = tickers.get("user_stocks")

def sp_tracker():
    base_url = "https://www.alphavantage.co/query"
    for ticker in tickers:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key_sp
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if "Global Quote" in data:
            price = data["Global Quote"]["05. price"]
            return f"{ticker}: {convert_currency(price, "USD", "RUB")}"
        else:
            return f"Ошибка получения данных для {ticker}"

def convert_currency(amount, from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        exchange_rate = data['conversion_rates'].get(to_currency)
        if exchange_rate:
            return amount * exchange_rate
        else:
            return "Currency not supported"
    else:
        return f"Error: {data.get('error', {}).get('info', 'Unknown error')}"

def day_time():
    current_datetime = datetime.datetime.now()
    hour = current_datetime.hour
    if 3 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 17:
        greeting = "Добрый день"
    elif 17 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    return greeting

def cards(operation_info):
    unique_cards = set()

    for operation in operation_info:
        card_number = operation.get("Номер карты")
        unique_cards.add(card_number)

    return list(unique_cards)

def summ(operation_info):
    summa = operation_info.get("Сумма платежа")
    return summa

def cashback(operation_info):
    summa = operation_info.get("Сумма платежа")
    cash_back = summa * 0.01
    return cash_back

def top_5_transactions(operation_info):
    top = []
    for summa in operation_info:
        money = summa.get("Сумма платежа")
        top.append(money)
    top.sort(reverse=True)
    return top[:5]

def currency_course(operation_info):
    amount = operation_info.get("Сумма операции")
    from_currency = operation_info.get("Валюта операции")
    correct_currency = convert_currency(amount, from_currency, "RUB")
    return correct_currency


def filter_by_date(date, output_file="../data/filtered_operations.json"):
    df = pd.read_excel("../data/operations.xlsx", engine="openpyxl")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    target_date = pd.to_datetime(date, format="%d.%m.%Y %H:%M:%S", dayfirst=True, errors="coerce")
    start_date = target_date.replace(day=1)
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= target_date)]
    filtered_df.to_json(output_file, orient="records", force_ascii=False, indent=4)
    return output_file

print(cards(read_json(filter_by_date("11.11.2019 11:11:11"))))




