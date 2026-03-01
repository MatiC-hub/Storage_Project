import os
import sys
import re
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# -------------------------
# DB Engine
# -------------------------
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


# -------------------------
# Helpers
# -------------------------
def to_str_or_none(x):
    """Return stripped string or None if missing/empty."""
    if x is None or pd.isna(x):
        return None
    s = str(x).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None
    return s


def normalize_bool(x):
    """Normalize booleans to 1/0/None."""
    if x is None or pd.isna(x):
        return None
    s = str(x).strip().lower()
    if s in ("true", "1", "yes", "y", "t"):
        return 1
    if s in ("false", "0", "no", "n", "f"):
        return 0
    return None


LOWER_WORDS = {
    "de", "del", "la", "las", "los", "y",
    "da", "das", "do", "dos",
    "van", "von", "der", "den", "di"
}


def normalize_name(s):
    """
    Normalize place/name strings:
    - strip
    - collapse multiple spaces
    - Title Case
    - keep connectors/prepositions in lowercase (de, del, la, etc.)
    """
    s = to_str_or_none(s)
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s)
    s = s.title()
    parts = s.split(" ")
    parts = [p.lower() if p.lower() in LOWER_WORDS else p for p in parts]
    return " ".join(parts)

def none_if_nan(v):
    """Convert any pandas/float NaN to None (MySQL-friendly)."""
    try:
        # pd.isna covers: np.nan, pd.NA, NaT, etc.
        return None if pd.isna(v) else v
    except Exception:
        return v
    
def get_snapshot_date_from_path(csv_path: str) -> str:
    parts = os.path.normpath(csv_path).split(os.sep)
    for i, p in enumerate(parts):
        if p == "raw" and i + 1 < len(parts):
            return parts[i + 1]
    return "unknown_date"

# -------------------------
# Main ETL
# -------------------------
def main(csv_path: str):
    print("RUNNING:", __file__)
    engine = build_engine()

    # 1) EXTRACT
    df = pd.read_csv(csv_path, sep=None, engine="python")
    df.columns = [c.strip() for c in df.columns]

    print("Columns sample:", df.columns[:20].tolist())

    # --- Normalize column names (support both "owner.*" exports and legacy exports)
    df.columns = (
        pd.Index(df.columns)
            .str.replace(r"^owner\.", "", regex=True)  # owner.id -> id
            .str.replace(r"^owner\.customFields\.", "customFields.", regex=True)  # (if it's needed in future exports)
    )

    # 2) VALIDATE (users.csv structure)
    required = [
        "id",
        "customFields.city",
        "customFields.province",
        "customFields.country",
        "customFields.nac",
        "customFields.isCompany",
        "customFields.business",
        "language",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV missing columns: {missing}\n"
            "Tip: asegúrate de exportar users/customers con customFields.*"
        )

    # 3) TRANSFORM — rename to DB-ready names
    df = df.rename(
        columns={
            "id": "external_owner_id",
            "customFields.city": "city",
            "customFields.province": "province",
            "customFields.country": "country",
            "customFields.nac": "nationality",
            "customFields.isCompany": "is_business_account",
            "customFields.business": "business_name_raw",
            "language": "language",
        }
    )

    # 3.1) Create columns that exist in DB but NOT in public CSV (PII)
    df["first_name"] = None
    df["last_name"] = None
    df["email_primary"] = None
    df["email_secondary"] = None
    df["phone_primary"] = None
    df["phone_secondary"] = None

    # 3.2) Normalize key fields
    df["external_owner_id"] = df["external_owner_id"].apply(to_str_or_none)
    df["is_business_account"] = df["is_business_account"].apply(normalize_bool)

    # 3.3) Clean place fields
    df["city"] = df["city"].apply(normalize_name)
    df["province"] = df["province"].apply(normalize_name)
    df["country"] = df["country"].apply(normalize_name)

    # --- Extra cleaning for city (remove numeric-only & leading apostrophes)
    df["city"] = df["city"].apply(lambda x: x.lstrip("'") if isinstance(x, str) else x)
    df.loc[df["city"].str.match(r"^\d+$", na=False), "city"] = None

    # --- Load Countries reference (variants -> standard)
    countries_path = os.path.join("data", "reference", "countries.csv")
    country_map = {}

    if os.path.exists(countries_path):
        cdf = pd.read_csv(countries_path)

        # Normalize both columns to ensure consistent comparison
        cdf["variant_norm"] = cdf["variant"].apply(normalize_name)
        cdf["standard_norm"] = cdf["country_standard"].apply(normalize_name)

        country_map = dict(zip(cdf["variant_norm"], cdf["standard_norm"]))

    # Apply country standardization: map known variants to their canonical form
        df["country"] = df["country"].apply(lambda x: country_map.get(x, x))

    # --- Load city aliases reference (variants -> standard)
    city_alias_path = os.path.join("data", "reference", "city_aliases.csv")

    if os.path.exists(city_alias_path):
        city_df = pd.read_csv(city_alias_path)

        city_df["variant_norm"] = city_df["city_variant"].apply(normalize_name)
        city_df["standard_norm"] = city_df["city_standard"].apply(normalize_name)

        city_map = dict(zip(city_df["variant_norm"], city_df["standard_norm"]))

        df["city"] = df["city"].apply(lambda x: city_map.get(x, x))

     # --- Load Spanish provinces reference
    ref_path = os.path.join("data", "reference", "spanish_provinces.csv")
    if os.path.exists(ref_path):
        ref_df = pd.read_csv(ref_path)
        spanish_provinces = set(
            ref_df["province"].dropna().apply(normalize_name)
        )
    else:
        spanish_provinces = set()

    # --- Auto-fill country = Spain if province is Spanish
    df.loc[
        df["province"].isin(spanish_provinces) & df["country"].isna(),
        "country"
    ] = "Spain"

    # Nationality comes already standardized by you (English) -> just strip/None
    df["nationality"] = df["nationality"].apply(to_str_or_none)

    # Language simple strip
    df["language"] = df["language"].apply(to_str_or_none)

    # --- 3.4) Business name handling
    # Business name is intentionally excluded from the public dataset.
    # It is always set to NULL, even if present in the source file.
    df["business_name"] = None

    # 3.5) Basic filters
    df = df.dropna(subset=["external_owner_id"]).copy()
    df = df.drop_duplicates(subset=["external_owner_id"], keep="last")

    print("Rows after cleaning:", len(df))
    if len(df) == 0:
        raise ValueError("No valid records to load after cleaning (external_owner_id empty).")
    
    # --- Export pending country review (country is NULL but city/province present)
    # Detect snapshot date from input path (e.g. data/raw/2026-02-25/owners_customers.csv)
    snapshot_date = None
    parts = os.path.normpath(csv_path).split(os.sep)
    for i, p in enumerate(parts):
        if p == "raw" and i + 1 < len(parts):
            snapshot_date = parts[i + 1]
            break
    if snapshot_date is None:
        snapshot_date = "unknown_date"

    # --- Load manual monthly customers if exists (same snapshot_date)
    manual_path = os.path.join("data", "raw", "manual", snapshot_date, "monthly_customer.csv")
    if os.path.exists(manual_path):
        print(f"📌 Loading manual customers: {manual_path}")
        df_manual = pd.read_csv(manual_path, sep=";", dtype=str)

        # Ensure required columns exist (in case of future edits)
        required_cols = ["external_owner_id", "nationality", "language", "city", "province", "country", "is_business_account"]
        for c in required_cols:
            if c not in df_manual.columns:
                df_manual[c] = None

        df = pd.concat([df, df_manual], ignore_index=True)
        print("Manual customers loaded:", len(df_manual))

        df = df.drop_duplicates(subset=["external_owner_id"], keep="last")

    snapshot_date = get_snapshot_date_from_path(csv_path)
    out_dir = os.path.join("data", "processed", snapshot_date)
    os.makedirs(out_dir, exist_ok=True)

        # --- Export pending country review (country is NULL but city/province present)
    pending = df.loc[
        df["country"].isna() & (df["city"].notna() | df["province"].notna()),
        ["city", "province"]
    ].copy()

    pending_report = (
        pending.fillna("")
        .groupby(["city", "province"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
        .sort_values("n", ascending=False)
    )

    # --- Detect snapshot date
    snapshot_date = get_snapshot_date_from_path(csv_path)

    # --- Create processed folder
    out_dir = os.path.join("data", "processed", snapshot_date)
    os.makedirs(out_dir, exist_ok=True)

    # --- Export pending country review
    pending = df.loc[
        df["country"].isna() & (df["city"].notna() | df["province"].notna()),
        ["city", "province"]
    ].copy()

    pending_report = (
        pending.fillna("")
        .groupby(["city", "province"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
        .sort_values("n", ascending=False)
    )

    pending_path = os.path.join(out_dir, "pending_country_review.csv")
    pending_report.to_csv(pending_path, index=False, encoding="utf-8")
    print(f"📄 Pending country review exported: {pending_path} ({len(pending_report)} rows)")
  

    # 4) LOAD prep (match your MySQL columns)
    final_cols = [
        "external_owner_id",
        "first_name",
        "last_name",
        "business_name",
        "is_business_account",
        "email_primary",
        "email_secondary",
        "phone_primary",
        "phone_secondary",
        "city",
        "province",
        "country",
        "nationality",
        "language",
    ]
    final_df = df[final_cols].copy()

    # Ensure is_business_account is 0/1 (default 0 if missing)
    final_df["is_business_account"] = (
        final_df["is_business_account"]
        .apply(lambda x: 1 if x == 1 else 0)
        .astype(int)
    )

    # Replace ANY pandas NaN/<NA> with Python None (MySQL-friendly)
    final_df = final_df.astype(object).where(pd.notna(final_df), None)

    # --- Export cleaned customers dataset
    out_dir = os.path.join("data", "processed", snapshot_date)
    os.makedirs(out_dir, exist_ok=True)
    customers_clean_path = os.path.join(out_dir, "customers_clean.csv")
    final_df.to_csv(customers_clean_path, index=False, encoding="utf-8")
    print(f"💾 Customers clean exported: {customers_clean_path}")

    # Safety: ensure no NaN survives into the dicts
    records = [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in final_df.to_dict(orient="records")
    ]

    # Quick quality prints
    print("Sample record:", records[0] if records else None)
    print("country NULL count:", int(final_df["country"].isna().sum()))
    print("province NULL count:", int(final_df["province"].isna().sum()))
    print("city NULL count:", int(final_df["city"].isna().sum()))

    # 5) LOAD (UPSERT by external_owner_id)
    upsert_sql = """
    INSERT INTO customers
    (external_owner_id, first_name, last_name, business_name, is_business_account,
     email_primary, email_secondary, phone_primary, phone_secondary,
     city, province, country, nationality, language)
    VALUES
    (:external_owner_id, :first_name, :last_name, :business_name, :is_business_account,
     :email_primary, :email_secondary, :phone_primary, :phone_secondary,
     :city, :province, :country, :nationality, :language)
    ON DUPLICATE KEY UPDATE
      first_name = VALUES(first_name),
      last_name = VALUES(last_name),
      business_name = VALUES(business_name),
      is_business_account = VALUES(is_business_account),
      email_primary = VALUES(email_primary),
      email_secondary = VALUES(email_secondary),
      phone_primary = VALUES(phone_primary),
      phone_secondary = VALUES(phone_secondary),
      city = VALUES(city),
      province = VALUES(province),
      country = VALUES(country),
      nationality = VALUES(nationality),
      language = VALUES(language);
    """

    with engine.begin() as conn:
        conn.execute(text(upsert_sql), records)

        total = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        matched = conn.execute(
            text("SELECT COUNT(*) FROM customers WHERE external_owner_id IS NOT NULL")
        ).scalar()

    print("✅ ETL customers OK")
    print(f"- Records loaded/updated: {len(records)}")
    print(f"- Customers in DB total: {total}")
    print(f"- Customers with external_owner_id: {matched}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python etl_customers.py path/to/users.csv")
        sys.exit(1)

    main(sys.argv[1])