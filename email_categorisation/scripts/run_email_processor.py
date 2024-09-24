import sys
import os
import asyncio
import imaplib
import email
from email.header import decode_header
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy import Column, String, Integer, DateTime

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logging configuration
logging.basicConfig(filename='logs/email_categorisation.log', level=logging.DEBUG)

# Database setup
DATABASE_URL = 'postgresql+asyncpg://email_user:12345@localhost/email_categorisation'
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Importing Email model from models/email.py
class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    category = Column(String)
    subject = Column(String)
    timestamp = Column(DateTime)

async def fetch_and_save_emails():
    logging.info("Starting email fetch process...")
    mail = None

    try:
        mail = imaplib.IMAP4_SSL('mail.deftboxsolutions.co.in', 993)
        mail.login('kishan@deftboxsolutions.co.in', 'VK1m$skocAVJ')
        logging.info("Logged in to IMAP server.")
        mail.select('inbox')

        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        logging.info(f"Total emails fetched: {len(email_ids)}")

        async with AsyncSessionLocal() as session:
            existing_emails_query = select(Email.email)
            existing_emails_result = await session.execute(existing_emails_query)
            existing_emails = {row[0] for row in existing_emails_result.scalars()}

            new_emails = []

            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                email_from = msg['From']
                subject = msg['Subject']

                decoded_subject, encoding = decode_header(subject)[0]
                if isinstance(decoded_subject, bytes):
                    subject = decoded_subject.decode(encoding if encoding else 'utf-8')

                logging.info(f"Fetched email: From: {email_from}, Subject: {subject}")

                if email_from not in existing_emails:
                    timestamp = int(email.utils.mktime_tz(email.utils.parsedate_tz(msg['Date']))) if msg['Date'] else None
                    new_emails.append({
                        'email': email_from,
                        'category': 'default_category',
                        'subject': subject,
                        'timestamp': timestamp
                    })

            if new_emails:
                logging.info(f"New emails to be saved: {len(new_emails)}")
                for email_data in new_emails:
                    existing_email_query = select(Email).where(Email.email == email_data['email'])
                    existing_email_result = await session.execute(existing_email_query)
                    if existing_email_result.scalars().first() is None:
                        insert_query = insert(Email).values(email_data)
                        await session.execute(insert_query)
                await session.commit()
                logging.info("New emails fetched and saved successfully.")
            else:
                logging.info("No new emails to save.")

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        if mail:
            mail.logout()
            logging.info("Logged out from IMAP server.")

if __name__ == "__main__":
    asyncio.run(fetch_and_save_emails())
