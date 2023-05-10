from pydantic import BaseModel
from datetime import datetime


class ValidDate(BaseModel):
    date: datetime
