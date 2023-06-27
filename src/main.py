from fastapi import FastAPI
from otodom import PageScraper
from fastapi.responses import JSONResponse
#import pandas as pd
import json
import logging
from db_connector import get_sqlmodel_engine, insert_flat_offer
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sql_models import FlatOffers

engine = get_sqlmodel_engine()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)



app = FastAPI()
ps = PageScraper()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# http://localhost:8000/docs

@app.get("/scrape_data", status_code=200)
async def insert_data():

    data = ps.run()
    inserted_enities_cnt = 0
    for item in data:
        try:
            insert_flat_offer(engine, item)
            inserted_enities_cnt += 1

        except Exception as err:
            logging.warning(f'Operation failed: \n {err}')

    output_dict = {
    "is_success": True if len(data) == inserted_enities_cnt else False,
    "total_enities": len(data),
    "inserted_enities": inserted_enities_cnt
    }

    output = JSONResponse(content=output_dict)

    return output

# @app.get("/newest_offer")
# async def func():
#     df = pd.read_csv("flats_data.csv", sep='\t')
#     df = df.fillna('')
#     output = df.to_dict("records") 
#     return output

# @app.get("/top_offer")
# async def func():
#     df = pd.read_csv("flats_data.csv", sep='\t')
#     df = df.fillna('')
#     output = df.to_dict("records") 
#     return output