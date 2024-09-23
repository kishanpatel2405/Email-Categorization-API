# email_processor.py
import asyncio
from core.event_handlers import process_emails

async def main():
    await process_emails()

if __name__ == "__main__":
    asyncio.run(main())
