import sys
from app.database import SessionLocal
from app.services.ingestion import IngestionService
from app.utils.logging import logger


def main():
    db = SessionLocal()
    try:
        service = IngestionService(db)
        result = service.run_ingestion()
        logger.info(f"Dataset Ingestion Finished Successfully: {result}")
    except Exception as e:
        logger.error(f"Dataset Ingestion Failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
