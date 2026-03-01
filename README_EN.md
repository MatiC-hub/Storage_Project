# 🗄️ Personal Project – Self-Storage Database

## 🎯 Project Objective

This project has a dual purpose:

### 1️⃣ Academic (Bootcamp & Portfolio)

Final project of a Data Analytics bootcamp aimed at:

- Designing a complete relational database from scratch.
- Building a reproducible ETL pipeline in Python.
- Applying data modeling, integrity, and governance best practices.
- Delivering a professional end-to-end analytics project.

### 2️⃣ Professional (Real Business Context)

The project is based on a real self-storage business environment.

The database is designed to be structured, maintainable, and scalable, supporting questions such as:

- Customer distribution by country.
- Minimum, average, and maximum length of stay.
- Current occupancy and temporal evolution.
- Active vs recently ended customer behavior.

⚠️ **Privacy Note:**  
All datasets published in this repository are synthetic.  
Real business data is processed locally only.

---

## 🏗️ Project Architecture

### 📂 Repository Structure

00_STORAGE_PROJECT/
│
├── data/
│   ├── raw/
│   │   ├── 2026-01-27/
│   │   │   ├── rentals.csv
│   │   │   ├── types.csv
│   │   │   └── units.csv
│   │   │
│   │   └── 2026-02-25/
│   │       ├── owners_customers.csv
│   │       └── rentals.csv
│   │
│   ├── processed/
│   │   ├── 2026-01-27/
│   │   │   └── units_clean.csv
│   │   │
│   │   └── 2026-02-25/
│   │       ├── customers_clean.csv
│   │       ├── rentals_clean.csv
│   │       └── pending_country_review.csv
│   │
│   └── reference/
│       ├── countries.csv
│       ├── spanish_provinces.csv
│       └── city_aliases.csv
│
├── images/
│   └── data_model.png
│
├── sql/
│   ├── Diagram.mwb
│   └── Revisiones.sql
│
├── src/
│   ├── etl_customers.py
│   ├── etl_rentals.py
│   └── etl_units.py
│
├── .env                # Not committed (credentials)
├── .gitignore
├── README_ES.md
└── README_EN.md

## 🗄️ Data Model

Database: `storage_project`

Main tables:

- `customers`
- `units`
- `rentals`
- `bulk_areas`
- `bulk_occupancies`

Clear separation between:

- Core entities (customers, physical storage)
- Temporal events (rentals, occupancies)

The ER diagram was generated using MySQL Workbench.

---

## 🔄 ETL Process

The ETL pipeline is implemented in Python and designed to be idempotent.

### Extract
- Read CSV exports from the external management system.
- Organize data by snapshot date.

### Transform
- Column harmonization.
- Type normalization.
- Duplicate removal.
- Invalid value cleaning.
- Geographic standardization using:
  - `countries.csv`
  - `spanish_provinces.csv`
  - `city_aliases.csv`
- Automatic country assignment (`Spain`) when province matches official Spanish provinces.
- Export of records requiring manual review (`pending_country_review.csv`).

### Load
- Insert/Upsert into MySQL using `INSERT ... ON DUPLICATE KEY UPDATE`.
- Post-load integrity checks.

---

## 🧹 Data Governance & Quality

The project includes:

- Full removal of personal identifiable information (PII) in the public repository.
- Referential integrity checks.
- Controlled NULL reduction.
- Snapshot versioning for reproducibility and historical comparison.

---

## 📊 Snapshots

Each ETL execution generates:

data/processed/<snapshot_date>/
customers_clean.csv
rentals_clean.csv
units_clean.csv
pending_country_review.csv


This enables:

- Reproducibility.
- Temporal comparisons.
- Evolution analysis.

---

## 🛠️ Tech Stack

- MySQL
- Python
- pandas
- SQLAlchemy
- python-dotenv
- Power BI (next phase)
- Tableau (next phase)

---

## 🚀 Current Status

- Relational model implemented.
- Customers, rentals, and units ETLs operational.
- Snapshot automation completed.
- Geographic standardization implemented.
- Database validated (no PII).
- Ready for analytical phase.