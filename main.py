from fastapi import FastAPI
from otodom import PageScraper
import asyncio
import pandas as pd

app = FastAPI()
ps = PageScraper()

@app.get("/api")
def root():
    return ps.get_data()

@app.get("/data")
def func():
    df = pd.read_csv("flats_data.csv", sep='\t')
    df = df.fillna('')
    output = df.to_dict("records") 
    return output