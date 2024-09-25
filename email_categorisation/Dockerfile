FROM ubuntu:latest
LABEL authors="deftbox"

ENTRYPOINT ["top", "-b"]

# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Install poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main

# Copy alembic folder and ini file
COPY alembic /app/alembic
COPY alembic.ini /app/

# Run migrations
RUN poetry run alembic upgrade head

# Copy the rest of your application code
COPY . /app/

# Expose the port your app runs on (e.g., 8000 for FastAPI)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
