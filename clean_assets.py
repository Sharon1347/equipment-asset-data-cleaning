import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)

INPUT  = "equipment_messy.csv"
OUTPUT = "equipment_cleaned.csv"

if __name__ == "__main__":
    log.info("Data Cleaning Script — starting")

    df = pd.read_csv(INPUT)
    log.info(f"Loaded: {len(df)} rows, {df.duplicated().sum()} duplicates, {df.isnull().sum().sum()} missing values")

    # 1. Remove duplicates
    df = df.drop_duplicates()

    # 2. Strip whitespace
    for col in df.select_dtypes(include="str").columns:
        df[col] = df[col].str.strip()

    # 3. Standardise capitalisation
    for col in ["MANUFACTURER", "ASSET TYPE", "AREA", "LOCATION", "CITY"]:
        if col in df.columns:
            df[col] = df[col].str.title()

    # 4. Standardise CONDITION — numeric to text
    condition_map = {0: "Unknown", 1: "Poor", 2: "Poor", 3: "Fair", 4: "Good", 5: "Excellent"}
    df["CONDITION"] = pd.to_numeric(df["CONDITION"], errors="coerce").map(condition_map).fillna("Unknown")

    # 5. Standardise date format
    df["CREATED"] = pd.to_datetime(df["CREATED"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 6. Fill missing values
    df["SERIAL"] = df["SERIAL"].fillna("UNKNOWN")
    df["MODEL"]  = df["MODEL"].fillna("UNKNOWN")

    # 7. Clean manufacturer names
    df["MANUFACTURER"] = df["MANUFACTURER"].str.replace(r"^\d+\s*-\s*", "", regex=True)

    # 8. Drop empty and irrelevant columns
    df = df.dropna(axis=1, how="all")
    df = df.drop(columns=[c for c in df.columns if "PHOTO" in c], errors="ignore")

    # Save
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    log.info(f"Done: {len(df)} clean rows saved to {OUTPUT}")
    log.info(f"After: {df.duplicated().sum()} duplicates, {df.isnull().sum().sum()} missing values")
    print(df[["MANUFACTURER", "ASSET TYPE", "CONDITION", "CREATED", "SERIAL", "AREA"]].head(10).to_string())