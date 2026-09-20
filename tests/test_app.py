from unittest.mock import MagicMock, patch

import pytest

from main import CurrencyConverterApp


@pytest.fixture
def app():
    instance = CurrencyConverterApp.__new__(CurrencyConverterApp)
    instance.loan_var = MagicMock()
    instance.loan_time_var = MagicMock()
    instance.annual_interest_var = MagicMock()
    instance.base_var = MagicMock()
    instance.target_var = MagicMock()
    instance.monthly_payment = 0.0
    instance.log = MagicMock()
    instance.monthly_label = MagicMock()
    instance.loan_sum_label = MagicMock()
    instance.interest_label = MagicMock()
    instance.result_label = MagicMock()
    instance.target_entry = MagicMock()
    yield instance


def test_calculate_loan_success(app):
    app.loan_var.get.return_value = "100000"
    app.loan_time_var.get.return_value = "12"
    app.annual_interest_var.get.return_value = "12"
    CurrencyConverterApp.calculate_loan(app)
    assert app.monthly_payment > 0


def test_calculate_loan_invalid_loan_amount(app):
    app.loan_var.get.return_value = "-5"
    app.loan_time_var.get.return_value = "12"
    app.annual_interest_var.get.return_value = "12"
    CurrencyConverterApp.calculate_loan(app)
    assert app.monthly_payment == 0.0


def test_convert_success(app):
    app.monthly_payment = 1000.0
    app.target_var.get.return_value = "USD"
    with patch("main.get_saved_rate", return_value=90.0):
        CurrencyConverterApp.convert(app)
    app.result_label.config.assert_called()


def test_convert_none_rate(app):
    app.monthly_payment = 1000.0
    app.target_var.get.return_value = "USD"
    with patch("main.get_saved_rate", return_value=None):
        CurrencyConverterApp.convert(app)
    app.log.assert_called()


def test_convert_exception(app):
    app.monthly_payment = 1000.0
    app.target_var.get.return_value = "USD"
    with patch("main.get_saved_rate", side_effect=Exception("boom")):
        with pytest.raises(Exception):
            CurrencyConverterApp.convert(app)


def test_update_db_success(app):
    fake = {"Valute": {"USD": {"Value": 90, "Nominal": 1}}}
    with patch("main.fetch_rates", return_value=fake), patch("main.save_rate"):
        CurrencyConverterApp.update_db(app)
    app.log.assert_called()


def test_update_db_empty_rates(app):
    with patch("main.fetch_rates", return_value={}):
        CurrencyConverterApp.update_db(app)
    app.log.assert_called()