from datetime import datetime
from sqlalchemy.future import select
from models.email import Email
from core.database import AsyncSessionLocal


async def process_emails():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Email))
            emails = result.scalars().all()

            print(f"Processing emails at {datetime.now()}")

            for email in emails:
                print(f"Processing email: {email.email}, category: {email.category}")

            await session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            await session.rollback()
