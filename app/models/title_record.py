from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Index
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class TitleRecord(Base):
    __tablename__ = "title_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    raw_domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="English", index=True)
    language_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="dataset_default")
    contact_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    faiss_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    cluster_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    phonetic_code: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    record_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_row_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        Index("idx_norm_title_domain", "normalized_title", "domain"),
    )


class DatasetIngestion(Base):
    __tablename__ = "dataset_ingestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sheet_name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_normalized_titles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_titles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    domain_counts_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_progress")
    report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
