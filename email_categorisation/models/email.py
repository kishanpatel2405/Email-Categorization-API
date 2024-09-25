from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, unique=True, index=True)
    sender_name = Column(String)
    category = Column(String)
    subject = Column(String)
    timestamp = Column(DateTime)
    attachments = Column(JSON)
