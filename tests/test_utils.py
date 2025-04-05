import json
from unittest.mock import mock_open

import pandas as pd
import pytest

from src.utils import read_json, read_xlsx

fake_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


@pytest.fixture
def valid_excel_file(tmp_path):
    data = {
        "Номер карты": ["1234", "5678", "91011"],
        "Сумма операции": [-100, -200, -300],
        "Категория": ["Еда", "Такси", "Развлечения"],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "operations.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return str(file_path)


@pytest.fixture
def invalid_excel_file(tmp_path):
    invalid_file_path = tmp_path / "invalid_operations.xlsx"
    with open(invalid_file_path, "w") as f:
        f.write("This is not a valid excel file.")
    return str(invalid_file_path)


def test_read_xlsx_valid(valid_excel_file):
    result = read_xlsx(valid_excel_file)

    expected_data = [
        {"Номер карты": 1234, "Сумма операции": -100, "Категория": "Еда"},
        {"Номер карты": 5678, "Сумма операции": -200, "Категория": "Такси"},
        {"Номер карты": 91011, "Сумма операции": -300, "Категория": "Развлечения"},
    ]

    assert result == expected_data


def test_read_xlsx_invalid(invalid_excel_file):
    result = read_xlsx(invalid_excel_file)

    assert result == []


def test_read_xlsx_file_not_found():
    non_existent_file = "../data/non_existent_file.xlsx"
    result = read_xlsx(non_existent_file)

    assert result == []


def test_read_json_successfully(mocker):

    mocker.patch("src.utils.open", mock_open(read_data=json.dumps(fake_data)))

    result = read_json("path/to/file.json")

    assert result == fake_data


def test_read_json_fails_on_exception(mocker):

    mocker.patch("src.utils.open", mock_open())

    mocker.patch("json.load", side_effect=Exception("JSON decoding error"))

    result = read_json("path/to/file.json")

    assert result == []
