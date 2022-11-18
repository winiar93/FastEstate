from fastapi import FastAPI
from otodom_scrape import get_page_content
import asyncio
app = FastAPI()


@app.get("/")
def root():
    return get_page_content()