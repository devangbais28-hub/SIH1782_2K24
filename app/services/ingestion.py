import json
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import engine, Base
from app.models.title_record import TitleRecord
from app.repositories.titles import TitleRepository
from app.scripts.validate_dataset import validate_dataset, DATASET_PATH, EXPECTED_SHEET
from app.utils.normalization import normalize_title, normalize_domain
from app.utils.phonetic import compute_phonetic_code
from app.utils.logging import logger


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TitleRepository(db)

    def run_ingestion(self, dataset_path: str = DATASET_PATH, force_clear: bool = True) -> dict:
        logger.info(f"Starting dataset ingestion for {dataset_path}...")
        
        # 1. Run validation
        val_report = validate_dataset(dataset_path)
        if not val_report["is_valid"]:
            raise ValueError(f"Dataset validation failed: {val_report['errors']}")

        # 2. Ensure schema exists
        Base.metadata.create_all(bind=engine)

        # 3. Create Audit Record
        audit_data = {
            "source_filename": dataset_path,
            "sheet_name": EXPECTED_SHEET,
            "total_rows": val_report["total_rows"],
            "valid_rows": val_report["valid_titles_count"],
            "invalid_rows": val_report["blank_titles_count"],
            "duplicate_normalized_titles": val_report["duplicate_normalized_titles_count"],
            "missing_titles": val_report["blank_titles_count"],
            "domain_counts_json": json.dumps(val_report["domain_counts"]),
            "started_at": datetime.now(timezone.utc),
            "status": "in_progress",
            "report_path": "output/dataset_validation_report.json"
        }
        audit = self.repo.create_ingestion_audit(audit_data)

        # Clear existing title records if forced
        if force_clear:
            logger.info("Clearing existing TitleRecord entries for fresh ingestion...")
            self.db.query(TitleRecord).delete()
            self.db.commit()

        # 4. Read excel file
        df = pd.read_excel(dataset_path, sheet_name=EXPECTED_SHEET)
        col_map = {c: str(c).strip().lower() for c in df.columns}
        df = df.rename(columns=col_map)

        records_to_insert = []
        for idx, row in df.iterrows():
            raw_title = str(row.get("titles", "")).strip()
            if not raw_title or raw_title.lower() == "nan":
                continue

            raw_desc = str(row.get("description", "")).strip()
            description = None if not raw_desc or raw_desc.lower() == "nan" else raw_desc

            raw_dom = str(row.get("domain", "")).strip()
            raw_domain = None if not raw_dom or raw_dom.lower() == "nan" else raw_dom
            domain = normalize_domain(raw_domain)

            raw_contact = str(row.get("contact_info", "")).strip()
            contact_info = None if not raw_contact or raw_contact.lower() == "nan" else raw_contact

            norm_title = normalize_title(raw_title)
            phonetic_code = compute_phonetic_code(raw_title)

            record = {
                "title": raw_title,
                "normalized_title": norm_title,
                "description": description,
                "domain": domain,
                "raw_domain": raw_domain,
                "language": "English",
                "language_source": "dataset_default",
                "contact_info": contact_info,
                "phonetic_code": phonetic_code,
                "record_status": "active",
                "source_file": dataset_path,
                "source_row_number": idx + 2,  # Header is row 1
            }
            records_to_insert.append(record)

        # 5. Bulk insert into database
        inserted_count = self.repo.bulk_create_title_records(records_to_insert, batch_size=1000)

        # 6. Finalize Audit Record
        completed_at = datetime.now(timezone.utc)
        self.repo.update_ingestion_audit(audit.id, {
            "completed_at": completed_at,
            "status": "completed",
            "valid_rows": inserted_count
        })

        logger.info(f"Successfully ingested {inserted_count} title records into database.")
        return {
            "audit_id": audit.id,
            "inserted_count": inserted_count,
            "total_rows": val_report["total_rows"],
            "status": "completed"
        }
