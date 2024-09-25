import os
import sys
import asyncio
import imaplib
import email
from datetime import datetime
from email.header import decode_header
import logging
from sqlalchemy.future import select
from sqlalchemy import insert
from email.utils import parseaddr, parsedate_tz, mktime_tz
from dotenv import load_dotenv
from prettytable import PrettyTable
from core.database import get_db
from models.email import Email
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

scheduler = BackgroundScheduler()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_categorisation.log')
    ]
)

ATTACHMENTS_DIR = 'data/attachments'
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


async def fetch_emails(mail):
    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()
    logging.info(f"Total emails fetched: {len(email_ids)}")
    return email_ids


async def process_email(mail, email_id):
    result, msg_data = mail.fetch(email_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    sender_name, sender_email = parseaddr(msg['From'])
    subject = msg['Subject']
    decoded_subject, encoding = decode_header(subject)[0]
    if isinstance(decoded_subject, bytes):
        subject = decoded_subject.decode(encoding if encoding else 'utf-8')
    logging.info(f"Fetched email: From: {sender_name}, Email: {sender_email}, Subject: {subject}")
    return {
        'email_id': sender_email,
        'sender_name': sender_name,
        'category': "spam" if 'spam' in subject.lower() else "inbox",
        'subject': subject,
        'timestamp': datetime.fromtimestamp(mktime_tz(parsedate_tz(msg['Date']))) if msg['Date'] else None,
        'attachments': []
    }


async def save_emails(session, new_emails):
    existing_emails_query = select(Email.email_id)
    existing_emails_result = await session.execute(existing_emails_query)
    existing_emails = {row[0] for row in existing_emails_result.scalars()}
    for email_data in new_emails:
        if email_data['email_id'] not in existing_emails:
            insert_query = insert(Email).values(email_data)
            await session.execute(insert_query)
            logging.info(f"Inserting email: {email_data}")
        else:
            logging.info(f"Email already exists, skipping: {email_data['email_id']}")
    await session.commit()


async def display_emails(new_emails):
    table = PrettyTable()
    table.field_names = ["Email ID", "Sender Name", "Category", "Subject", "Timestamp"]
    for email_data in new_emails:
        timestamp_str = email_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if email_data['timestamp'] else None
        table.add_row([
            email_data['email_id'],
            email_data['sender_name'] if email_data['sender_name'] else None,
            email_data['category'],
            email_data['subject'],
            timestamp_str
        ])
    print(table)


async def fetch_and_save_emails():
    try:
        mail_server = os.getenv('MAIL_SERVER')
        mail_user = os.getenv('MAIL_USER')
        mail_password = os.getenv('MAIL_PASSWORD')
        mail = imaplib.IMAP4_SSL(mail_server, os.getenv('IMAP_PORT'))
        mail.login(mail_user, mail_password)
        logging.info("Logged in to IMAP server.")
        mail.select('inbox')
        email_ids = await fetch_emails(mail)
        new_emails = []
        for email_id in email_ids:
            email_data = await process_email(mail, email_id)
            new_emails.append(email_data)
        async for session in get_db():
            await save_emails(session, new_emails)
        await display_emails(new_emails)
        logging.info("New emails fetched and saved successfully.")
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if mail:
            mail.logout()
            logging.info("Logged out from IMAP server.")


if __name__ == "__main__":
    scheduler.add_job(
        lambda: asyncio.run(fetch_and_save_emails()),
        CronTrigger.from_crontab('* * * * *')
    )
    scheduler.start()
