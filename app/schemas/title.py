from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TitleRecordSchema(BaseModel):
    id: int
    title: str
    normalized_title: str
    description: Optional[str] = None
    domain: str
    raw_domain: Optional[str] = None
    language: str
    language_source: Optional[str] = None
    contact_info: Optional[str] = None
    faiss_position: Optional[int] = None
    phonetic_code: Optional[str] = None
    record_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
