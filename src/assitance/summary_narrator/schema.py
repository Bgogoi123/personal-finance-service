from pydantic import BaseModel
from datetime import datetime


class SummaryGeneratorPayloadSchema(BaseModel):
    date: datetime | None
