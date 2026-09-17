"""SQL - Models and persistence for fiscal invoices."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class NotaFiscal(Base):
    """Model for fiscal invoice records."""

    __tablename__ = "notas_fiscais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, index=True)
    fornecedor: Mapped[str] = mapped_column(String(255), nullable=False)
    data_emissao: Mapped[datetime] = mapped_column(Date, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    arquivo_origem: Mapped[str] = mapped_column(String(255), nullable=False)
    data_processamento: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    def __repr__(self) -> str:
        return (
            f"<NotaFiscal(cnpj={self.cnpj}, fornecedor={self.fornecedor}, "
            f"valor={self.valor}, data_emissao={self.data_emissao})>"
        )


class Database:
    """Database manager for notas_fiscais."""

    def __init__(self, db_path: str | Path = "data/fiscal.db"):
        self.db_path = Path(db_path)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.SessionFactory = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)

    def save_nota_fiscal(
        self,
        cnpj: str,
        fornecedor: str,
        data_emissao: datetime,
        valor: float,
        arquivo_origem: str,
    ) -> NotaFiscal:
        """Save a fiscal invoice record to the database."""
        with Session(self.engine) as session:
            nota = NotaFiscal(
                cnpj=cnpj,
                fornecedor=fornecedor,
                data_emissao=data_emissao,
                valor=valor,
                arquivo_origem=arquivo_origem,
            )
            session.add(nota)
            session.commit()
            session.refresh(nota)
            return nota

    def get_all_notas(self) -> list[NotaFiscal]:
        """Retrieve all fiscal invoices."""
        with Session(self.engine) as session:
            return list(session.query(NotaFiscal).all())

    def get_notas_by_cnpj(self, cnpj: str) -> list[NotaFiscal]:
        """Retrieve fiscal invoices by CNPJ."""
        with Session(self.engine) as session:
            return list(session.query(NotaFiscal).filter(NotaFiscal.cnpj == cnpj).all())
