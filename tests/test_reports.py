import json
import os

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture(scope="module")
def transactions():
    return pd.DataFrame(
        {
            "Дата платежа": ["01.01.2025", "01.01.2025", "02.01.2025", "03.01.2025"],
            "Категория": ["Такси", "Еда", "Такси", "Супермаркеты"],
            "Сумма операции": [-777, -555, -1312, -666],
        }
    )


@pytest.fixture(scope="module", autouse=True)
def cleanup_file():
    if os.path.exists("../report_decor.json"):
        os.remove("../report_decor.json")
    yield
    if os.path.exists("../report_decor.json"):
        os.remove("../report_decor.json")


@pytest.mark.parametrize(
    "category, expected",
    [
        ("Еда", pd.DataFrame({"Категория": ["Еда"], "Сумма трат": [555]})),
    ],
)
def test_spending_by_category(transactions, category, expected):
    spending_by_category(transactions, category, "01.01.2025")

    with open("../report_decor.json", "r", encoding="utf-8") as file:
        data_from_file = json.load(file)
    actual_result = pd.DataFrame([data_from_file], columns=["Категория", "Сумма трат"])
    pd.testing.assert_frame_equal(actual_result, expected)
