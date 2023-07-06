import json
import logging

from otodom import PageScraper
from sql_models import FlatOffers

from fastapi import FastAPI
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, desc
import pandas as pd
from db_connector import DBConnector
import pyodbc
from typing import Any


import logging

logging.getLogger().setLevel(logging.INFO)

db = DBConnector()
engine = db.get_sqlmodel_engine()
db_session = db.get_session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/scrape_data", status_code=200)
async def insert_data(
    session: Session = Depends(db_session),
    min_price: int = 300000,
    max_price: int = 450000,
) -> JSONResponse:
    ps = PageScraper(min_price=min_price, max_price=max_price)
    logging.info(f"Running web page scraper ...")
    data = ps.run()
    inserted_enities_cnt = 0
    logging.info(f"Updating database.")
    for item in data:
        try:
            db.insert_flat_offer(item)
            inserted_enities_cnt += 1

        except Exception as err:
            logging.warning(f"Operation failed: \n {err}")

    logging.info(f"Updating offers ranking.")
    with open("./sql_scripts/offer_ranking.sql") as file:
        query = text(file.read())
        session.execute(query)
        session.commit()

    output_dict = {
        "is_success": True if len(data) == inserted_enities_cnt else False,
        "total_enities": len(data),
        "inserted_enities": inserted_enities_cnt,
    }

    output = JSONResponse(content=output_dict)
    return output


@app.get("/get_data")
async def get_data(
    session: Session = Depends(db_session),
    page_size: int = 10,
    page: int = 0,
    rank_order: bool = True,
) -> Any:
    stmt = select(FlatOffers)

    if page_size:
        stmt = stmt.limit(page_size)
    if page:
        stmt = stmt.offset(page * page_size)
    if rank_order:
        stmt = stmt.order_by(desc(FlatOffers.rank))

    data = session.exec(stmt).all()

    reject_list = ["investment_estimated_delivery", "created_at", "updated_at"]

    content = [
        {key: value for key, value in d.__dict__.items() if key not in reject_list}
        for d in data
    ]

    return content


@app.get("/get_file")
async def get_data() -> FileResponse:
    file_name = "offers_of_flats.csv"
    stmt = select(FlatOffers)
    df = pd.read_sql_query(stmt, con=engine)
    logging.info(f"Data successfully loaded.")
    df.to_csv(file_name, sep="\t")
    engine.dispose()
    logging.info(f"Output saved into csv file.")
    return FileResponse(
        file_name, media_type="application/octet-stream", filename=file_name
    )


@app.get("/sync_db")
async def sync(session: Session = Depends(db_session)) -> None:
    conn = pyodbc.connect(
        "DRIVER={FreeTDS};SERVER=mssql;PORT=1433;DATABASE=otodom;UID=SA;PWD=Welcome1",
        autocommit=True,
    )
    cur = conn.cursor()
    stmt = select(FlatOffers)
    data = session.exec(stmt).all()
    cur.execute("Truncate table otodom.dbo.flat_offers;")
    for row in data:
        try:
            insert_stmt = f"""INSERT INTO otodom.dbo.flat_offers
            (offer_id, offer_title, street, location, total_price, area_square_meters,
            date_created, offer_url, agency_name, rooms_number, investment_estimated_delivery, price_per_square_meter)
            VALUES({row.offer_id},
            '{row.offer_title}',
            '{row.street}',
            '{row.location}',
            '{row.total_price}',
            '{row.area_square_meters}',
            '{row.created_at}',
            '{row.offer_url}',
            '{row.agency_name}',
            '{row.rooms_number}',
            '{row.investment_estimated_delivery}', 
            '{row.price_per_square_meter}');"""
            cur.execute(insert_stmt)
        except pyodbc.IntegrityError as int_err:
            logging.warning(f"Error occured during inserting data /n ERROR: {int_err}")
        else:
            logging.info(f'Inserted row with ID = {row.dict().get("offer_id")}')

    cur.close()
    conn.close()
