from fastapi import FastAPI
import asyncio
from scripts.fetch_emails import scheduler
app = FastAPI()


@app.get("/")
async def read_root():
    return {"NO": "NOOOO"}


@app.on_event("startup")
async def startup_event():
    scheduler.start()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)