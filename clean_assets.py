import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)

REPORT = "cleaning_report.txt"
INPUT = "raw_equipment_data.csv"
OUTPUT = "cleaned_output.csv"

if __name__ == "__main__":
    log.info("Data Cleaning Script — starting")

    df = pd.read_csv(INPUT)

    before_rows = len(df)
    before_duplicates = df.duplicated().sum()
    before_missing = df.isnull().sum().sum()

    log.info(
        f"Loaded: {before_rows} rows, {before_duplicates} duplicates, "
        f"{before_missing} missing values"
    )

    # 1. Remove duplicates
    df = df.drop_duplicates()

    # 2. Strip whitespace
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # 3. Standardize capitalization
    for col in ["MANUFACTURER", "ASSET TYPE", "AREA", "LOCATION", "CITY"]:
        if col in df.columns:
            df[col] = df[col].str.title()

    # 4. Standardize CONDITION — numeric to text
    if "CONDITION" in df.columns:
        condition_map = {
            0: "Unknown",
            1: "Poor",
            2: "Poor",
            3: "Fair",
            4: "Good",
            5: "Excellent",
        }
        df["CONDITION"] = (
            pd.to_numeric(df["CONDITION"], errors="coerce")
            .map(condition_map)
            .fillna("Unknown")
        )

    # 5. Standardize date format
    if "CREATED" in df.columns:
        df["CREATED"] = pd.to_datetime(df["CREATED"], errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )

    # 6. Fill missing values
    for col in ["SERIAL", "MODEL"]:
        if col in df.columns:
            df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
            df[col] = df[col].fillna("UNKNOWN")

    # 7. Clean manufacturer names
    if "MANUFACTURER" in df.columns:
        df["MANUFACTURER"] = df["MANUFACTURER"].str.replace(
            r"^\d+\s*-\s*", "", regex=True
        )

    # 8. Drop empty and irrelevant columns
    df = df.dropna(axis=1, how="all")
    df = df.drop(columns=[c for c in df.columns if "PHOTO" in c.upper()], errors="ignore")

    after_rows = len(df)
    after_duplicates = df.duplicated().sum()
    after_missing = df.isnull().sum().sum()

    # Save cleaned output
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    # Save cleaning report
    report = f"""Equipment Asset Data Cleaning Report

Rows before cleaning: {before_rows}
Rows after cleaning: {after_rows}

Duplicate rows before cleaning: {before_duplicates}
Duplicate rows after cleaning: {after_duplicates}

Missing values before cleaning: {before_missing}
Missing values after cleaning: {after_missing}

Key cleaning steps:
- Removed duplicate rows
- Stripped whitespace from text fields
- Standardized capitalization
- Mapped numeric condition codes to descriptive labels
- Standardized dates
- Filled missing serial/model values with UNKNOWN
- Removed empty and photo-related columns
"""

    with open(REPORT, "w", encoding="utf-8") as file:
        file.write(report)

    log.info(f"Done: {after_rows} clean rows saved to {OUTPUT}")
    log.info(f"Cleaning report saved to {REPORT}")
    log.info(f"After: {after_duplicates} duplicates, {after_missing} missing values")

    preview_cols = [
        col
        for col in ["MANUFACTURER", "ASSET TYPE", "CONDITION", "CREATED", "SERIAL", "AREA"]
        if col in df.columns
    ]

    if preview_cols:
        print(df[preview_cols].head(10).to_string(index=False))