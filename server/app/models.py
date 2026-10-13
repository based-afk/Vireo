from sqlalchemy import Column, BigInteger, Integer, String, Numeric, Date, DateTime, func
from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(String(10), nullable=False)
    category = Column(String(60), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
