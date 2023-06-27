    
from sqlalchemy import select, text
from typing import List, Dict, Any
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.dialects.postgresql import insert
from sql_models import FlatOffers
import logging
from datetime import datetime

pg_user = "postgres"
pg_dbname = "postgres"
pg_password = "Welcome1"
pg_host = "postgres"
pg_port = 5432
pg_con_string = (
    f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}"
)

def insert_flat_offer(engine, item):
    conn = engine.connect()
    stmt = (
        insert(FlatOffers)
        .values(item)
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[FlatOffers.offer_id],
        set_={'price_per_square_meter': item['price_per_square_meter'], 
              'total_price': item['total_price'],
              'updated_at': datetime.now()},
    )

    conn.execute(stmt)
    conn.commit()
    conn.close()


def get_sqlmodel_engine():
    engine = create_engine(pg_con_string)
    return engine

def get_session():
    engine = get_sqlmodel_engine()
    with Session(engine) as session:
        yield session

def test():
    engine = get_sqlmodel_engine()
    conn = engine.connect() 
    logging.info('ok')
    conn.close()


