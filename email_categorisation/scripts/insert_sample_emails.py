import asyncio
from core.database import AsyncSessionLocal
from models.email import Email


async def insert_sample_emails():
    async with AsyncSessionLocal() as session:
        sample_emails = [
            Email(email="test1@example.com", category="inbox"),
            Email(email="test2@example.com", category="spam"),
            Email(email="test3@example.com", category="promotions"),
        ]

        session.add_all(sample_emails)
        await session.commit()
        print("Sample emails inserted successfully!")

if __name__ == "__main__":
    asyncio.run(insert_sample_emails())
