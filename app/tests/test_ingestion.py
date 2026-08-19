import pytest
from app.database import engine, Base, SessionLocal
from app.models.title_record import TitleRecord, DatasetIngestion
from app.scripts.validate_dataset import validate_dataset

def test_validation_passes_for_real_dataset():
    report = validate_dataset()
    assert report["is_valid"] is True
    assert report["valid_titles_count"] >= 6000

def test_validation_fails_for_missing_file():
    report = validate_dataset("data/nonexistent.xlsx")
    assert report["is_valid"] is False
    assert len(report["errors"]) > 0

def test_ingested_records_exist():
    """Requires ingest_dataset to have been run."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(TitleRecord).filter(
            TitleRecord.record_status == "active"
        ).count()
        assert count >= 6000, f"Expected >= 6000 active records, got {count}"
    finally:
        db.close()

def test_ingestion_audit_exists():
    db = SessionLocal()
    try:
        audit = db.query(DatasetIngestion).first()
        assert audit is not None
        assert audit.status == "completed"
        assert audit.valid_rows >= 6000
    finally:
        db.close()

def test_spot_check_normalized_domain():
    db = SessionLocal()
    try:
        rec = db.query(TitleRecord).filter(
            TitleRecord.domain == "news-sports"
        ).first()
        assert rec is not None, "Expected at least one news-sports record"
    finally:
        db.close()
