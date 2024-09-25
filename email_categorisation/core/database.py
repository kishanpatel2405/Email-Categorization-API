# core/database.py
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv('DATABASE_URL')
logging.info(f"DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL is None:
    logging.error("DATABASE_URL is not set in the environment variables.")
    raise ValueError("DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

