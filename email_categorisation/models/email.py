from sqlalchemy import Column, String, Integer, DateTime
from core.database import Base


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)  # Ensure this is unique if you're avoiding duplicates
    category = Column(String)
    subject = Column(String)
    timestamp = Column(DateTime)
