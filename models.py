import datetime # for future validation of dates
from typing import Optional
from pydantic import BaseModel, validator


class Flight(BaseModel):
    flight_origin: Optional[str]
    flight_destination: Optional[str]
    flight_airline: Optional[str]
    flight_official_date: Optional[str]
    flight_number: Optional[str]
    flight_status: Optional[str]
    flight_real_date: Optional[str]

    @validator('flight_destination', pre=True, always=True)
    def validate_flight_destination(cls, value):
        # Add validation logic if necessary
        return value