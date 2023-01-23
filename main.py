from fastapi import FastAPI
from otodom import PageScraper
import asyncio
import pandas as pd


ps = PageScraper()
app = FastAPI()


@app.get("/api")
async def root(page_limit: int = 100):
    return ps.get_data(page_limit=page_limit)

@app.get("/data")
async def func():
    df = pd.read_csv("flats_data.csv", sep='\t')
    df = df.fillna('')
    output = df.to_dict("records") 
    return output
