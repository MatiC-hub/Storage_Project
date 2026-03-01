import os
import sys
import math
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


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
    """Keep external ids as STRING. Empty/NaN -> None."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s != "" else None


def to_float_or_none(x):
    """Parse float safely. Empty/NaN/invalid -> None."""
    if pd.isna(x):
        return None
    try:
        # handle comma decimals just in case
        s = str(x).strip().replace(",", ".")
        if s == "":
            return None
        v = float(s)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def guess_unit_type(volume_m3: float | None) -> str:
    """
    Heurística simple por volumen (m3).
    Ajusta los cortes si luego quieres afinar.
    """
    if volume_m3 is None:
        # Si no hay volumen, mejor lo metemos como "small" (o el mínimo que acepte tu enum)
        return "small"

    v = volume_m3
    if v <= 1.5:
        return "locker"
    if v <= 4.0:
        return "small"
    if v <= 8.0:
        return "medium"
    if v <= 15.0:
        return "large"
    return "extra_large"


def main(csv_path: str):
    print(">>> RUNNING:", __file__)
    print(">>> CSV:", csv_path)

    engine = build_engine()

    # 1) EXTRACT
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    print("Columns:", df.columns.tolist())

    # 2) TRANSFORM - rename to DB-friendly names
    # CSV: id,typeId,name,floor,width,length,height,measure,area,volume,state,created,updated
    df = df.rename(
        columns={
            "id": "external_unit_id",
            "typeId": "external_type_id",
            "name": "unit_number",
            "state": "unit_state",
        }
    )

    # 3) Clean / normalize
    df["external_unit_id"] = df["external_unit_id"].apply(to_str_or_none)
    df["external_type_id"] = df["external_type_id"].apply(to_str_or_none)

    # floor puede ser texto (lo dejamos tal cual, pero limpio)
    if "floor" in df.columns:
        df["floor"] = df["floor"].apply(to_str_or_none)

    # medidas (en tu CSV measure viene vacío; asumimos metros)
    df["width_m"] = df["width"].apply(to_float_or_none) if "width" in df.columns else None
    df["length_m"] = df["length"].apply(to_float_or_none) if "length" in df.columns else None
    df["height_m"] = df["height"].apply(to_float_or_none) if "height" in df.columns else None

    # volumen: preferimos el volume del CSV (parece venir en m3)
    df["cubic_meters"] = df["volume"].apply(to_float_or_none) if "volume" in df.columns else None

    # si cubic_meters falta, lo calculamos
    def calc_volume(row):
        if row.get("cubic_meters") is not None:
            return row.get("cubic_meters")
        w, l, h = row.get("width_m"), row.get("length_m"), row.get("height_m")
        if w is None or l is None or h is None:
            return None
        return w * l * h

    df["cubic_meters"] = df.apply(calc_volume, axis=1)

    # unit_type por heurística
    df["unit_type"] = df["cubic_meters"].apply(guess_unit_type)

    # 4) Filter invalid rows
    before = len(df)
    df = df.dropna(subset=["external_unit_id"]).copy()
    df = df.drop_duplicates(subset=["external_unit_id"], keep="last")
    after = len(df)

    print(f"Rows before filter: {before} | after filter/dedup: {after}")
    if after == 0:
        raise ValueError("No valid unit records after cleaning. Check CSV 'id' column.")

    # 5) Keep only final cols for DB
    final_cols = [
        "external_unit_id",
        "external_type_id",
        "unit_number",
        "floor",
        "height_m",
        "width_m",
        "length_m",
        "cubic_meters",
        "unit_type",
        "unit_state",
    ]

    final_df = df[final_cols].copy()

    # IMPORTANT: convert pandas NaN -> None (MySQL hates NaN)
    final_df = final_df.where(pd.notna(final_df), None)

    # --- Detect snapshot date from input path
    snapshot_date = None
    parts = os.path.normpath(csv_path).split(os.sep)
    for i, p in enumerate(parts):
        if p == "raw" and i + 1 < len(parts):
            snapshot_date = parts[i + 1]
            break
    if snapshot_date is None:
        snapshot_date = "unknown_date"

    # --- Export cleaned units dataset
    out_dir = os.path.join("data", "processed", snapshot_date)
    os.makedirs(out_dir, exist_ok=True)
    units_clean_path = os.path.join(out_dir, "units_clean.csv")
    final_df.to_csv(units_clean_path, index=False, encoding="utf-8")
    print(f"💾 Units clean exported: {units_clean_path}")

    records = final_df.to_dict(orient="records")

    # Debug seguro (sin datos sensibles)
    # Unidades no son PII, pero aun así mostramos sólo métricas
    nan_counts = {k: sum(1 for r in records if r.get(k) is None) for k in final_cols}
    print("NULL counts (None) by column:", nan_counts)

    # 6) LOAD (UPSERT)
    upsert_sql = """
    INSERT INTO units
    (external_unit_id, external_type_id, unit_number, floor,
     height_m, width_m, length_m, cubic_meters, unit_type, unit_state)
    VALUES
    (:external_unit_id, :external_type_id, :unit_number, :floor,
     :height_m, :width_m, :length_m, :cubic_meters, :unit_type, :unit_state)
    ON DUPLICATE KEY UPDATE
        external_type_id = VALUES(external_type_id),
        unit_number = VALUES(unit_number),
        floor = VALUES(floor),
        height_m = VALUES(height_m),
        width_m = VALUES(width_m),
        length_m = VALUES(length_m),
        cubic_meters = VALUES(cubic_meters),
        unit_type = VALUES(unit_type),
        unit_state = VALUES(unit_state);
    """

    with engine.begin() as conn:
        conn.execute(text(upsert_sql), records)

        total = conn.execute(text("SELECT COUNT(*) FROM units")).scalar()
        matched = conn.execute(text("SELECT COUNT(*) FROM units WHERE external_unit_id IS NOT NULL")).scalar()

    print("✅ ETL units OK")
    print(f"- Records loaded/updated: {len(records)}")
    print(f"- Units in DB (total): {total}")
    print(f"- Units with external_unit_id: {matched}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python etl\\etl_units.py data_real\\exports_storeganise\\units_YYYYMMDD.csv")

    main(sys.argv[1])