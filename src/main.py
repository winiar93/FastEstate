import json
import logging

from otodom import PageScraper
from sql_models import FlatOffers

from fastapi import FastAPI
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse

from sqlmodel import Field, Session, SQLModel, create_engine, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, desc

from db_connector import get_sqlmodel_engine, insert_flat_offer, get_session




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
async def insert_data(session: Session = Depends(get_session)):

    data = ps.run()
    inserted_enities_cnt = 0
    for item in data:
        try:
            insert_flat_offer(engine, item)
            inserted_enities_cnt += 1

        except Exception as err:
            logging.warning(f'Operation failed: \n {err}')


    with open("./sql_scripts/offer_ranking.sql") as file:
        query = text(file.read())
        session.execute(query)
        session.commit()

    output_dict = {
    "is_success": True if len(data) == inserted_enities_cnt else False,
    "total_enities": len(data),
    "inserted_enities": inserted_enities_cnt
    }

    output = JSONResponse(content=output_dict)
    return output

@app.get("/get_data")
async def get_data(session: Session = Depends(get_session), page_size: int = 10, page: int = 0, rank_order: bool = True):
    stmt = select(FlatOffers)

    if page_size:
        stmt = stmt.limit(page_size)
    if page: 
        stmt = stmt.offset(page*page_size)
    if rank_order:
        stmt = stmt.order_by(desc(FlatOffers.rank))
    
    data = session.exec(stmt).all()
    
    reject_list  = ['investment_estimated_delivery', 'created_at', 'updated_at']

    content = [{key: value for key, value in d.__dict__.items() if key not in reject_list} for d in data]
    return content