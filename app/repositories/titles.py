from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.title_record import TitleRecord, DatasetIngestion


class TitleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, record_id: int) -> Optional[TitleRecord]:
        return self.db.query(TitleRecord).filter(TitleRecord.id == record_id).first()

    def get_by_ids(self, record_ids: List[int]) -> List[TitleRecord]:
        if not record_ids:
            return []
        return self.db.query(TitleRecord).filter(TitleRecord.id.in_(record_ids)).all()

    def get_by_exact_normalized_title(self, normalized_title: str) -> List[TitleRecord]:
        return self.db.query(TitleRecord).filter(
            TitleRecord.normalized_title == normalized_title,
            TitleRecord.record_status.in_(["active", "approved"])
        ).all()

    def get_all_active_titles(self) -> List[TitleRecord]:
        return self.db.query(TitleRecord).filter(
            TitleRecord.record_status.in_(["active", "approved"])
        ).order_by(TitleRecord.id.asc()).all()

    def get_by_cluster_ids(self, cluster_ids: List[int]) -> List[TitleRecord]:
        if not cluster_ids:
            return []
        return self.db.query(TitleRecord).filter(
            TitleRecord.cluster_id.in_(cluster_ids),
            TitleRecord.record_status.in_(["active", "approved"])
        ).all()

    def update_cluster_ids(self, id_to_cluster: dict) -> int:
        updated = 0
        for record_id, cid in id_to_cluster.items():
            rec = self.get_by_id(record_id)
            if rec:
                rec.cluster_id = cid
                updated += 1
        self.db.commit()
        return updated

    def create_title_record(self, record_data: dict) -> TitleRecord:
        record = TitleRecord(**record_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def bulk_create_title_records(self, records_data: List[dict], batch_size: int = 1000) -> int:
        if not records_data:
            return 0

        inserted_count = 0
        for i in range(0, len(records_data), batch_size):
            batch = records_data[i:i + batch_size]
            objects = [TitleRecord(**item) for item in batch]
            self.db.bulk_save_objects(objects)
            self.db.commit()
            inserted_count += len(batch)

        return inserted_count

    def update_faiss_positions(self, id_to_position_map: dict) -> int:
        updated = 0
        for record_id, position in id_to_position_map.items():
            rec = self.get_by_id(record_id)
            if rec:
                rec.faiss_position = position
                updated += 1
        self.db.commit()
        return updated

    def create_ingestion_audit(self, audit_data: dict) -> DatasetIngestion:
        audit = DatasetIngestion(**audit_data)
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def update_ingestion_audit(self, audit_id: int, update_data: dict) -> Optional[DatasetIngestion]:
        audit = self.db.query(DatasetIngestion).filter(DatasetIngestion.id == audit_id).first()
        if not audit:
            return None

        for k, v in update_data.items():
            setattr(audit, k, v)

        self.db.commit()
        self.db.refresh(audit)
        return audit
