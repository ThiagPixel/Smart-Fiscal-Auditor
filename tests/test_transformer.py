"""Unit tests for Transformer module."""

import pytest
from datetime import datetime

from src.transformer import Transformer


class TestTransformer:
    """Tests for the Transformer class."""

    def setup_method(self):
        self.t = Transformer()

    def test_clean_cnpj_with_formatting(self):
        assert self.t.clean_cnpj("12.345.678/0001-90") == "12345678000190"

    def test_clean_cnpj_without_formatting(self):
        assert self.t.clean_cnpj("12345678000190") == "12345678000190"

    def test_clean_cnpj_invalid(self):
        assert self.t.clean_cnpj("") == ""

    def test_validate_cnpj_valid(self):
        # Valid CNPJ: 44.852.175/0001-00
        assert self.t.validate_cnpj("44.852.175/0001-00") is True

    def test_validate_cnpj_valid_no_formatting(self):
        # Valid CNPJ: 44.852.175/0001-00 (unformatted)
        assert self.t.validate_cnpj("44852175000100") is True

    def test_validate_cnpj_invalid(self):
        assert self.t.validate_cnpj("12.345.678/0001-99") is False

    def test_validate_cnpj_too_short(self):
        assert self.t.validate_cnpj("12345678") is False

    def test_parse_date_dd_mm_yyyy(self):
        result = self.t.parse_date("15/03/2024")
        assert result == datetime(2024, 3, 15)

    def test_parse_date_yyyy_mm_dd(self):
        result = self.t.parse_date("2024-03-15")
        assert result == datetime(2024, 3, 15)

    def test_parse_date_invalid(self):
        assert self.t.parse_date("invalid") is None

    def test_parse_value_with_currency(self):
        result = self.t.parse_value("R$ 4.500,00")
        assert result == 4500.0

    def test_parse_value_with_dots_and_commas(self):
        result = self.t.parse_value("R$ 12.350,00")
        assert result == 12350.0

    def test_parse_value_simple(self):
        result = self.t.parse_value("1000.50")
        assert result == 1000.50

    def test_parse_value_invalid(self):
        assert self.t.parse_value("invalid") is None

    def test_transform_valid_data(self):
        data = {
            "cnpj": "44.852.175/0001-00",
            "fornecedor": "Tech Solutions",
            "data_emissao": "15/03/2024",
            "valor": "R$ 4.500,00",
        }
        result = self.t.transform(data)
        assert result is not None
        assert result["cnpj"] == "44852175000100"
        assert result["fornecedor"] == "Tech Solutions"
        assert result["data_emissao"] == datetime(2024, 3, 15)
        assert result["valor"] == 4500.0

    def test_transform_invalid_cnpj(self):
        data = {
            "cnpj": "99.999.999/9999-99",
            "fornecedor": "Test",
            "data_emissao": "15/03/2024",
            "valor": "R$ 100,00",
        }
        result = self.t.transform(data)
        assert result is None

    def test_transform_missing_fields(self):
        data = {"cnpj": "12.345.678/0001-90"}
        result = self.t.transform(data)
        assert result is None
