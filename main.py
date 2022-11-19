from fastapi import FastAPI
from otodom import get_data
import asyncio
app = FastAPI()


@app.get("/api")
def root():
    return get_data()