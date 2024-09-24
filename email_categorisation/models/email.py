from sqlalchemy import Column, String, Integer, DateTime, JSON
from core.database import Base

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, unique=True)
    sender_name = Column(String)
    category = Column(String)
    subject = Column(String)
    timestamp = Column(DateTime)
    attachments = Column(JSON)