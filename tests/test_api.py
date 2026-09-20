from unittest.mock import patch

import requests

from api import fetch_rates


def test_fetch_rates_success():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"Valute": {"USD": {"Value": 90}}}
        mock_get.return_value.raise_for_status.return_value = None
        result = fetch_rates()
    assert result["Valute"]["USD"]["Value"] == 90


def test_fetch_rates_success_without_success_field():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"Valute": {}}
        mock_get.return_value.raise_for_status.return_value = None
        result = fetch_rates()
    assert "Valute" in result


def test_fetch_rates_http_error():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError()
        assert fetch_rates() == {}


def test_fetch_rates_connection_error():
    with patch("api.requests.get", side_effect=requests.ConnectionError):
        assert fetch_rates() == {}


def test_fetch_rates_timeout_error():
    with patch("api.requests.get", side_effect=requests.Timeout):
        assert fetch_rates() == {}


def test_fetch_rates_empty_valute():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"Valute": {}}
        mock_get.return_value.raise_for_status.return_value = None
        assert fetch_rates()["Valute"] == {}


def test_fetch_rates_malformed_json():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.side_effect = ValueError("bad json")
        assert fetch_rates() == {}


def test_fetch_rates_ssl_error():
    with patch("api.requests.get", side_effect=requests.exceptions.SSLError):
        assert fetch_rates() == {}
