"""Unit tests for Database module."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from src.database import Database, NotaFiscal


class TestDatabase:
    """Tests for the Database class."""

    def setup_method(self):
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.create_tables()

    def teardown_method(self):
        # Close database connection before deleting
        self.db.engine.dispose()
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_create_tables(self):
        # Tables should already be created in setup
        notas = self.db.get_all_notas()
        assert notas == []

    def test_save_nota_fiscal(self):
        nota = self.db.save_nota_fiscal(
            cnpj="12345678000190",
            fornecedor="Test Company",
            data_emissao=datetime(2024, 3, 15),
            valor=4500.0,
            arquivo_origem="test.txt",
        )
        assert nota.id is not None
        assert nota.cnpj == "12345678000190"
        assert nota.fornecedor == "Test Company"
        assert nota.valor == 4500.0

    def test_get_all_notas(self):
        self.db.save_nota_fiscal(
            cnpj="12345678000190",
            fornecedor="Company 1",
            data_emissao=datetime(2024, 1, 1),
            valor=1000.0,
            arquivo_origem="test1.txt",
        )
        self.db.save_nota_fiscal(
            cnpj="98765432000199",
            fornecedor="Company 2",
            data_emissao=datetime(2024, 2, 2),
            valor=2000.0,
            arquivo_origem="test2.txt",
        )
        notas = self.db.get_all_notas()
        assert len(notas) == 2

    def test_get_notas_by_cnpj(self):
        self.db.save_nota_fiscal(
            cnpj="12345678000190",
            fornecedor="Company 1",
            data_emissao=datetime(2024, 1, 1),
            valor=1000.0,
            arquivo_origem="test1.txt",
        )
        self.db.save_nota_fiscal(
            cnpj="12345678000190",
            fornecedor="Company 2",
            data_emissao=datetime(2024, 2, 2),
            valor=2000.0,
            arquivo_origem="test2.txt",
        )
        notas = self.db.get_notas_by_cnpj("12345678000190")
        assert len(notas) == 2
