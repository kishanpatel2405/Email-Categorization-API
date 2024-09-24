import os
import sys
import asyncio
import imaplib
import email
from datetime import datetime
from email.header import decode_header
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy import insert, Column, String, Integer, DateTime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(filename='logs/email_categorisation.log', level=logging.DEBUG)

DATABASE_URL = 'postgresql+asyncpg://email_user:12345@localhost/email_categorisation'
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, unique=True)
    sender_name = Column(String)
    category = Column(String)
    subject = Column(String)
    timestamp = Column(DateTime)
    attachments = Column(String)


ATTACHMENTS_DIR = 'data/attachments'
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


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
            existing_emails_query = select(Email.email_id)
            existing_emails_result = await session.execute(existing_emails_query)
            existing_emails = {row[0] for row in existing_emails_result.scalars()}

            new_emails = []

            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                sender_name, email_id = email.utils.parseaddr(msg['From'])
                if not sender_name:
                    sender_name = "Unknown Sender"

                subject = msg['Subject']
                decoded_subject, encoding = decode_header(subject)[0]
                if isinstance(decoded_subject, bytes):
                    subject = decoded_subject.decode(encoding if encoding else 'utf-8')

                logging.info(f"Fetched email: From: {sender_name}, Email: {email_id}, Subject: {subject}")

                attachments = []
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join(ATTACHMENTS_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            attachments.append(filepath)

                if not attachments:
                    attachments = ["No Attachments"]

                if email_id not in existing_emails:
                    if msg['Date']:
                        timestamp = int(email.utils.mktime_tz(email.utils.parsedate_tz(msg['Date'])))
                        timestamp = datetime.fromtimestamp(timestamp)
                    else:
                        timestamp = None

                    new_emails.append({
                        'email_id': email_id,
                        'sender_name': sender_name,
                        'category': 'default_category',
                        'subject': subject,
                        'timestamp': timestamp,
                        'attachments': ','.join(attachments)
                    })

            if new_emails:
                logging.info(f"New emails to be saved: {len(new_emails)}")
                for email_data in new_emails:
                    existing_email_query = select(Email).where(Email.email_id == email_data['email_id'])
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


