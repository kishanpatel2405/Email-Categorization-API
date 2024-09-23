from sqlalchemy import Column, Integer, String
from core.database import Base


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    category = Column(String)
