"""ETL - Data cleaning, validation and standardization."""

import re
from datetime import datetime
from typing import Optional


class Transformer:
    """ETL transformer for fiscal invoice data."""

    @staticmethod
    def clean_cnpj(cnpj: str) -> str:
        """Remove formatting from CNPJ, leaving only digits."""
        return re.sub(r"\D", "", cnpj)

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Validate Brazilian CNPJ using the check digits algorithm."""
        cnpj = Transformer.clean_cnpj(cnpj)

        if len(cnpj) != 14:
            return False

        # Check for known invalid CNPJs (all same digit)
        if cnpj == cnpj[0] * 14:
            return False

        # Validate first check digit (position 13)
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
        digit1 = (sum1 * 10) % 11
        if digit1 == 10:
            digit1 = 0
        if digit1 != int(cnpj[12]):
            return False

        # Validate second check digit (position 14)
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum2 = sum(int(cnpj[i]) * weights2[i] for i in range(13))
        digit2 = (sum2 * 10) % 11
        if digit2 == 10:
            digit2 = 0
        if digit2 != int(cnpj[13]):
            return False

        return True

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse Brazilian date format (DD/MM/YYYY) to datetime."""
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def parse_value(value_str: str) -> Optional[float]:
        """Parse Brazilian currency format (R$ 1.234,56) to float."""
        # Remove currency symbols and spaces
        value_str = re.sub(r"[R$\s]", "", value_str)
        # Handle both . and , as separators
        # If both exist, . is thousands separator, , is decimal
        if "." in value_str and "," in value_str:
            value_str = value_str.replace(".", "").replace(",", ".")
        elif "," in value_str:
            value_str = value_str.replace(",", ".")
        elif "." in value_str and "," not in value_str:
            # Only dot present - could be US decimal (1000.50) or Brazilian thousands (1.000)
            parts = value_str.split(".")
            # If last part has exactly 2 digits and second-to-last part has 3 digits,
            # it's likely Brazilian thousands separator (e.g., 1.000,00 without the comma)
            if len(parts[-1]) == 2 and len(parts[-2]) == 3:
                value_str = value_str.replace(".", "")
            # Otherwise treat as US decimal format (e.g., 1000.50)
            # keep the dot

        try:
            return float(value_str)
        except ValueError:
            return None

    def transform(self, data: dict) -> dict | None:
        """
        Transform and validate raw invoice data.

        Returns cleaned data dict or None if validation fails.
        """
        errors = []

        # Clean and validate CNPJ
        raw_cnpj = data.get("cnpj", "")
        cnpj = self.clean_cnpj(raw_cnpj)
        if not cnpj:
            errors.append("CNPJ is required")
        elif not self.validate_cnpj(cnpj):
            errors.append(f"Invalid CNPJ: {raw_cnpj}")

        # Clean and validate fornecedor
        fornecedor = data.get("fornecedor", "").strip()
        if not fornecedor:
            errors.append("Fornecedor is required")

        # Parse and validate date
        data_emissao = None
        raw_date = data.get("data_emissao", "")
        if raw_date:
            data_emissao = self.parse_date(raw_date)
        if not data_emissao:
            errors.append(f"Invalid date format: {raw_date}")

        # Parse and validate value
        valor = None
        raw_value = data.get("valor", "")
        if raw_value:
            valor = self.parse_value(raw_value)
        if valor is None:
            errors.append(f"Invalid value: {raw_value}")
        elif valor < 0:
            errors.append(f"Negative value not allowed: {raw_value}")

        if errors:
            print(f"[TRANSFORMER] Validation errors: {errors}")
            return None

        return {
            "cnpj": cnpj,
            "fornecedor": fornecedor,
            "data_emissao": data_emissao,
            "valor": valor,
        }
