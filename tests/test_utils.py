import json
from unittest.mock import mock_open

from src.utils import read_json

fake_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


def test_read_json_successfully(mocker):

    mocker.patch("src.utils.open", mock_open(read_data=json.dumps(fake_data)))

    result = read_json("path/to/file.json")

    assert result == fake_data


def test_read_json_fails_on_exception(mocker):

    mocker.patch("src.utils.open", mock_open())

    mocker.patch("json.load", side_effect=Exception("JSON decoding error"))

    result = read_json("path/to/file.json")

    assert result == []
