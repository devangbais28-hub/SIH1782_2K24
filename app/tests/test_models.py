import pytest
from app.database import engine, Base, SessionLocal
from app.models.title_record import TitleRecord

def test_create_title_record_with_cluster_id():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        rec = TitleRecord(
            title="Test Title Cluster", normalized_title="test title cluster",
            domain="test", language="English", record_status="active",
            cluster_id=5
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        assert rec.cluster_id == 5
        result = db.query(TitleRecord).filter(TitleRecord.title == "Test Title Cluster").first()
        assert result is not None
        assert result.title == "Test Title Cluster"
    finally:
        db.close()
