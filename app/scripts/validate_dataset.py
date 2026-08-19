import os
import sys
import json
import pandas as pd
from collections import Counter
from datetime import datetime, timezone
from app.utils.normalization import normalize_title, normalize_domain
from app.utils.logging import logger

DATASET_PATH = os.path.join("data", "dataset_combined_all_6000-v2.xlsx")
EXPECTED_SHEET = "Combined Dataset"
REQUIRED_COLUMNS = ["titles", "description", "domain", "contact_info"]
MIN_VALID_TITLES = 6000
OUTPUT_DIR = "output"


def validate_dataset(dataset_path: str = DATASET_PATH) -> dict:
    logger.info(f"Starting dataset validation for: {dataset_path}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report = {
        "dataset_path": dataset_path,
        "sheet_name": EXPECTED_SHEET,
        "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        "file_exists": False,
        "sheet_exists": False,
        "columns_valid": False,
        "total_rows": 0,
        "valid_titles_count": 0,
        "blank_titles_count": 0,
        "missing_descriptions_count": 0,
        "missing_contact_info_count": 0,
        "duplicate_raw_titles_count": 0,
        "duplicate_normalized_titles_count": 0,
        "min_title_length": 0,
        "max_title_length": 0,
        "empty_domains_count": 0,
        "domain_counts": {},
        "is_valid": False,
        "errors": []
    }

    if not os.path.exists(dataset_path):
        err = f"Dataset file not found at: {dataset_path}"
        logger.error(err)
        report["errors"].append(err)
        return report

    report["file_exists"] = True

    try:
        xl = pd.ExcelFile(dataset_path)
        if EXPECTED_SHEET not in xl.sheet_names:
            err = f"Expected sheet '{EXPECTED_SHEET}' not found in {dataset_path}. Available sheets: {xl.sheet_names}"
            logger.error(err)
            report["errors"].append(err)
            return report

        report["sheet_exists"] = True
        df = pd.read_excel(dataset_path, sheet_name=EXPECTED_SHEET)
    except Exception as e:
        err = f"Failed to read dataset workbook/sheet: {str(e)}"
        logger.error(err)
        report["errors"].append(err)
        return report

    # Check columns
    df_cols = [str(c).strip().lower() for c in df.columns]
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df_cols]
    if missing_cols:
        err = f"Missing required columns: {missing_cols}. Found columns: {list(df.columns)}"
        logger.error(err)
        report["errors"].append(err)
        return report

    report["columns_valid"] = True
    report["total_rows"] = len(df)

    # Normalize column names in dataframe
    col_map = {c: str(c).strip().lower() for c in df.columns}
    df = df.rename(columns=col_map)

    # Validate titles
    raw_titles = df['titles'].astype(str).tolist()
    valid_titles = []
    normalized_titles = []
    title_lengths = []
    blank_titles = 0

    for idx, raw in enumerate(raw_titles):
        val = raw.strip()
        if not val or val.lower() == "nan":
            blank_titles += 1
            continue

        valid_titles.append(val)
        norm = normalize_title(val)
        normalized_titles.append(norm)
        title_lengths.append(len(val))

    report["valid_titles_count"] = len(valid_titles)
    report["blank_titles_count"] = blank_titles
    report["min_title_length"] = min(title_lengths) if title_lengths else 0
    report["max_title_length"] = max(title_lengths) if title_lengths else 0

    # Descriptions & Contact Info
    descriptions = df['description'].fillna('').astype(str).tolist()
    contacts = df['contact_info'].fillna('').astype(str).tolist()

    report["missing_descriptions_count"] = sum(1 for d in descriptions if not d.strip() or d.lower() == "nan")
    report["missing_contact_info_count"] = sum(1 for c in contacts if not c.strip() or c.lower() == "nan")

    # Duplicates
    raw_counts = Counter(valid_titles)
    norm_counts = Counter(normalized_titles)

    report["duplicate_raw_titles_count"] = sum(count - 1 for count in raw_counts.values() if count > 1)
    report["duplicate_normalized_titles_count"] = sum(count - 1 for count in norm_counts.values() if count > 1)

    # Domains
    raw_domains = df['domain'].fillna('').astype(str).tolist()
    norm_domains = []
    empty_domains = 0

    for dom in raw_domains:
        norm_dom = normalize_domain(dom)
        if norm_dom in ("unknown", ""):
            empty_domains += 1
        norm_domains.append(norm_dom)

    report["empty_domains_count"] = empty_domains
    report["domain_counts"] = dict(Counter(norm_domains))

    # Threshold Check
    if report["valid_titles_count"] < MIN_VALID_TITLES:
        err = f"Valid title count ({report['valid_titles_count']}) is less than required minimum ({MIN_VALID_TITLES})."
        logger.error(err)
        report["errors"].append(err)

    report["is_valid"] = len(report["errors"]) == 0

    # Write report files
    json_path = os.path.join(OUTPUT_DIR, "dataset_validation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    csv_path = os.path.join(OUTPUT_DIR, "dataset_validation_report.csv")
    flat_data = [{k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in report.items()}]
    pd.DataFrame(flat_data).to_csv(csv_path, index=False)

    logger.info(f"Validation report saved to {json_path} and {csv_path}")
    logger.info(f"Validation Result: {'PASSED' if report['is_valid'] else 'FAILED'}")

    return report


if __name__ == "__main__":
    rep = validate_dataset()
    if not rep["is_valid"]:
        sys.exit(1)
    sys.exit(0)
