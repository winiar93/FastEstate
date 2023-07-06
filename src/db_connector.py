from sqlalchemy import select, text
from typing import List, Dict, Any
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from sql_models import FlatOffers
import logging
from datetime import datetime
import logging

logging.getLogger().setLevel(logging.INFO)

pg_user = "postgres"
pg_dbname = "postgres"
pg_password = "Welcome1"
pg_host = "postgres"
pg_port = 5432
pg_con_string = (
    f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}"
)


class DBConnector:
    def __init__(
        self,
        pg_user="postgres",
        pg_dbname="postgres",
        pg_password="Welcome1",
        pg_host="postgres",
        pg_port=5432,
    ) -> None:
        self.pg_user = pg_user
        self.pg_dbname = pg_dbname
        self.pg_password = pg_password
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_con_string = f"postgresql+psycopg2://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_dbname}"
        self.engine = self.get_sqlmodel_engine()

    def get_sqlmodel_engine(self):
        engine = create_engine(pg_con_string)
        return engine

    def insert_flat_offer(self, item):
        try:
            conn = self.engine.connect()
            stmt = insert(FlatOffers).values(item)

            stmt = stmt.on_conflict_do_update(
                index_elements=[FlatOffers.offer_id],
                set_={
                    "price_per_square_meter": item["price_per_square_meter"],
                    "total_price": item["total_price"],
                    "updated_at": datetime.now(),
                },
            )

            conn.execute(stmt)
            logging.info(f'Item with id = {item.get("offer_id")} upserted.')
            conn.commit()
            conn.close()
        except SQLAlchemyError as e:
            logging.warning(f"Error in processing data: \n {e} \n Item: {item}")

    def get_session(self):
        engine = self.get_sqlmodel_engine()
        with Session(engine) as session:
            yield session

    def test(self):
        engine = self.get_sqlmodel_engine()
        conn = engine.connect()
        logging.info("ok")
        conn.close()
