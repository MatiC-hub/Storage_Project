import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


print(">>> RUNNING:", __file__)


def build_engine():
    load_dotenv()
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME", "storage_project")

    if not password:
        raise ValueError("Missing DB_PASSWORD in .env")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)


def to_str_or_none(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s != "" else None


def to_float_or_none(x):
    if pd.isna(x):
        return None
    try:
        return float(x)
    except Exception:
        return None


def to_date_or_none(x):
    if pd.isna(x):
        return None
    # pandas Timestamp -> python date
    try:
        return pd.to_datetime(x).date()
    except Exception:
        return None


def to_datetime_or_none(x):
    if pd.isna(x):
        return None
    try:
        return pd.to_datetime(x).to_pydatetime()
    except Exception:
        return None


def main(csv_path: str):
    engine = build_engine()

    print(">>> CSV:", csv_path)
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    print("Columns sample:", df.columns.tolist())

    # Rename CSV columns -> DB/external fields
    df = df.rename(
        columns={
            "rental.id": "external_rental_id",
            "rental.unitId": "external_unit_id",
            "rental.ownerId": "external_owner_id",
            "rental.state": "rental_state",
            "rental.price": "price_eur",
            "rental.deposit": "deposit_eur",
            "rental.startDate": "move_in_date",
            "rental.endDate": "move_out_date",
            "rental.billedUntil": "billed_until",
            "rental.created": "created_at",
            "rental.updated": "updated_at",
        }
    )

    required = [
        "external_rental_id",
        "external_unit_id",
        "external_owner_id",
        "rental_state",
        "price_eur",
        "deposit_eur",
        "move_in_date",
        "move_out_date",
        "billed_until",
        "created_at",
        "updated_at",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    # Normalize types
    df["external_rental_id"] = df["external_rental_id"].apply(to_str_or_none)
    df["external_unit_id"] = df["external_unit_id"].apply(to_str_or_none)
    df["external_owner_id"] = df["external_owner_id"].apply(to_str_or_none)

    df["price_eur"] = df["price_eur"].apply(to_float_or_none)
    df["deposit_eur"] = df["deposit_eur"].apply(to_float_or_none)

    df["move_in_date"] = df["move_in_date"].apply(to_date_or_none)
    df["move_out_date"] = df["move_out_date"].apply(to_date_or_none)
    df["billed_until"] = df["billed_until"].apply(to_date_or_none)

    df["created_at"] = df["created_at"].apply(to_datetime_or_none)
    df["updated_at"] = df["updated_at"].apply(to_datetime_or_none)

    # Drop rows without the natural key
    df = df.dropna(subset=["external_rental_id"]).copy()

    # Deduplicate by external key
    df = df.drop_duplicates(subset=["external_rental_id"], keep="last")

    print("Rows after clean/dedup:", len(df))
    if len(df) == 0:
        raise ValueError("No valid rental records after cleaning.")

    # IMPORTANT:
    # customer_id & unit_id are internal FKs and we are NOT resolving them here yet.
    # Table MUST allow NULL in customer_id/unit_id (ALTER TABLE you ran).
    df["customer_id"] = None
    df["unit_id"] = None

    # --- Detect snapshot date from input path
    snapshot_date = None
    parts = os.path.normpath(csv_path).split(os.sep)

    for i, p in enumerate(parts):
        if p == "raw" and i + 1 < len(parts):
            snapshot_date = parts[i + 1]
            break

    if snapshot_date is None:
        snapshot_date = "unknown_date"

    # --- Load manual rentals if exist
    manual_path = os.path.join("data", "raw", "manual", snapshot_date, "monthly_rentals.csv")

    if os.path.exists(manual_path):
        print(f"📦 Loading manual rentals: {manual_path}")
        df_manual = pd.read_csv(manual_path, sep=";", dtype=str)
        df = pd.concat([df, df_manual], ignore_index=True)
        print("Manual rows loaded:", len(df_manual))

    if "billing_type" not in df.columns:
        df["billing_type"] = None

    df["billing_type"] = (
        df.get("billing_type")
        .astype(str)
        .str.strip()
        .replace({"": None, "nan": None, "None": None})
    )
    df["billing_type"] = df["billing_type"].fillna("28_days")

    # Billing_type
    if "billing_type" not in df.columns:
        df["billing_type"] = None

    df["billing_type"] = df["billing_type"].fillna("28_days")

    df["customer_id"] = None
    df["unit_id"] = None

    final_cols = [
        "external_rental_id",
        "external_unit_id",
        "external_owner_id",
        "customer_id",
        "unit_id",
        "rental_state",
        "price_eur",
        "deposit_eur",
        "move_in_date",
        "move_out_date",
        "billed_until",
        "created_at",
        "updated_at",
        "billing_type",
    ]

    # Replace pandas NaN/NaT with None
    final_df = df[final_cols].copy()
    final_df = final_df.where(pd.notna(final_df), None)

    # --- Export cleaned rentals dataset
    out_dir = os.path.join("data", "processed", snapshot_date)
    os.makedirs(out_dir, exist_ok=True)
    rentals_clean_path = os.path.join(out_dir, "rentals_clean.csv")
    final_df.to_csv(rentals_clean_path, index=False, encoding="utf-8")
    print(f"💾 Rentals clean exported: {rentals_clean_path}")

    records = final_df.to_dict(orient="records")

    print("Sample record:", records[0])

    upsert_sql = """
    INSERT INTO unit_rentals (
        external_rental_id,
        external_unit_id,
        external_owner_id,
        customer_id,
        unit_id,
        rental_state,
        price_eur,
        deposit_eur,
        move_in_date,
        move_out_date,
        billed_until,
        created_at,
        updated_at
    )
    VALUES (
        :external_rental_id,
        :external_unit_id,
        :external_owner_id,
        :customer_id,
        :unit_id,
        :rental_state,
        :price_eur,
        :deposit_eur,
        :move_in_date,
        :move_out_date,
        :billed_until,
        :created_at,
        :updated_at
    )
    ON DUPLICATE KEY UPDATE
        external_unit_id = VALUES(external_unit_id),
        external_owner_id = VALUES(external_owner_id),
        rental_state = VALUES(rental_state),
        price_eur = VALUES(price_eur),
        deposit_eur = VALUES(deposit_eur),
        move_in_date = VALUES(move_in_date),
        move_out_date = VALUES(move_out_date),
        billed_until = VALUES(billed_until),
        updated_at = VALUES(updated_at);
    """

    print("SQL placeholders check: expecting keys like customer_id/unit_id...")
    print("Sample record keys:", sorted(records[0].keys()) if records else "NO RECORDS")
    
    with engine.begin() as conn:
        conn.execute(text(upsert_sql), records)

        total = conn.execute(text("SELECT COUNT(*) FROM unit_rentals")).scalar()
        with_ext = conn.execute(
            text("SELECT COUNT(*) FROM unit_rentals WHERE external_rental_id IS NOT NULL")
        ).scalar()

    print("✅ ETL rentals OK")
    print(f"- Records loaded/updated: {len(records)}")
    print(f"- Rentals in DB (total): {total}")
    print(f"- Rentals with external_rental_id: {with_ext}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python etl_rentals.py <path_to_csv>")
    main(sys.argv[1])