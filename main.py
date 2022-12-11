from fastapi import FastAPI
from otodom import get_data
import asyncio
import pandas as pd
app = FastAPI()


@app.get("/api")
def root():
    return get_data()

@app.get("/data")
def func():
    df = pd.read_csv("flats_data.csv", sep='\t')
    output = df.to_dict("records") 
    return output