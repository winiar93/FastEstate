from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union

from pydantic import validator
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Column, Field, SQLModel


class FlatOffers(SQLModel, table=True):

    __tablename__ = "flat_offers"
    offer_id: int = Field(default=None, primary_key=True)
    offer_title: Optional[str] = None
    street: Optional[str] = None
    location: Optional[str] = None
    total_price: Optional[float] = None
    area_square_meters: Optional[float] = None
    date_created_in_service: Optional[str] = None
    offer_url: Optional[str] = None
    agency_name: Optional[str] = None
    rooms_number: Optional[str] = None
    investment_estimated_delivery: Optional[str] = None
    price_per_square_meter: Optional[float] = None
    rank: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
