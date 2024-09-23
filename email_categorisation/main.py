# main.py
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess

app = FastAPI()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: subprocess.run(['python3', 'email_processor.py']), 'interval', seconds=1000)
    scheduler.start()


@app.on_event("startup")
async def startup_event():
    start_scheduler()


# Add your routes here
@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

