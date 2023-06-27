from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union

from pydantic import validator
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Column, Field, SQLModel


class FlatOffers(SQLModel, table=True):
    """
    Model describes a schema for HubSpot Contact stored in idflow2 database.

    Obligatory parameters:
        - hubspot_id - HubSpot object ID, unique for each object.
        - marketing_consent_optin - string ("true" or "false") or boolean value (true or false) - marketing consent
    """

    __tablename__ = "flat_offers"
    offer_id: int = Field(default=None, primary_key=True)
    offer_title: Optional[str] = None
    street: Optional[str] = None
    location: Optional[str] = None
    total_price: Optional[str] = None
    area_square_meters: Optional[str] = None
    date_created_in_service: Optional[str] = None 
    offer_url: Optional[str] = None
    agency_name: Optional[str] = None
    rooms_number: Optional[str] = None
    investment_estimated_delivery: Optional[str] = None
    price_per_square_meter: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
