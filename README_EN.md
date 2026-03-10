# 🗄️ Storage Facility Analytical System

![Python](https://img.shields.io/badge/Python-Data%20Pipeline-blue)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-purple)
![ETL](https://img.shields.io/badge/ETL-Pipeline-green)
![Data Analytics](https://img.shields.io/badge/Data-Analytics-lightgrey)

---

# Self-Storage Facility Data Platform

End-to-end data analytics project for a real self-storage facility.

The project builds a complete analytical system including:

• data/ Raw operational data ingestion  
• src/ Python ETL pipeline  
• sql/ Database model and validation queries   
• tableau/ BI dashboards  
• docs/ Project documentation and reports  

The goal is to transform operational data into actionable insights about:

• Occupancy and unit utilization  
• Customer behaviour and rental duration  
• Geographic distribution of demand  
• Customer segmentation

---

## 🎯 Project Objective

This project has two complementary goals:

### Academic Purpose

Final project of a Data Analytics bootcamp focused on designing a complete analytical system from raw operational data.

Key learning objectives include:

• Relational database modeling  
• Building a reproducible ETL pipeline in Python  
• Implementing data quality validation  
• Applying best practices in data governance and documentation  

### Business Case

The project was developed using real operational data from a self-storage facility.

The objective is to transform operational data into insights that support decision-making in areas such as:

• Facility occupancy and utilization  
• Customer behaviour and retention  
• Geographic demand distribution  
• Unit turnover and vacancy analysis

⚠️ **Privacy Note:**  
The data published in this repository is synthetic.  
Real operational data is processed only in a private local environment.

---

## 🏗 Data Architecture

The system follows a batch ETL architecture based on dated operational snapshots.

Raw Data → Python ETL → MySQL Database → Analytical SQL Layer → Tableau Dashboards

---

## 🔄 General Flow

### 1️⃣ Extract
- CSV exports from the operational system.
- Organized by date:
    data/raw/YYYY-MM-DD/


---

### 2️⃣ Transform
Independent scripts per entity:

- `etl_units.py`
- `etl_customers.py`
- `etl_rentals.py`

Includes:

- Data cleaning
- State normalization
- Geographic standardization
- Structural validation
- Referential integrity checks
- Inconsistency reporting

---

### 3️⃣ Load
- Insert / Upsert using `INSERT ... ON DUPLICATE KEY UPDATE`
- Referential integrity validation after load
- Foreign keys based on `external_*_id`

---

### 4️⃣ Analytical Layer
- Consolidated MySQL relational database
- SQL validation queries
- Prepared for BI tools (Tableau / Power BI)

---

## 📂 Repository Structure

The repository is organized following a typical data engineering workflow:

data/
Raw and processed snapshots used by the ETL pipeline.

src/
Python ETL scripts for units, customers and rentals.

sql/
Database model, validation queries and analytical views.

tableau/
Tableau workbooks used for the analytical dashboards.

images/
Project diagrams and visual assets.

reports/
Analytical documentation and project reports.
---

00_STORAGE_PROJECT/
│
├── data/
│ ├── raw/
│ │ ├── 2026-01-27/
│ │ │ ├── rentals.csv
│ │ │ ├── types.csv
│ │ │ └── units.csv
│ │ │
│ │ ├── 2026-02-25/
│ │ │ ├── owners_customers.csv
│ │ │ └── rentals.csv
│ │ │
│ │ └── 2026-02-28/
│ │ ├── owners_customers.csv
│ │ ├── rentals.csv
│ │ └── units.csv
│ │
│ ├── processed/
│ │ ├── 2026-01-27/
│ │ │ └── units_clean.csv
│ │ │
│ │ ├── 2026-02-25/
│ │ │ ├── customers_clean.csv
│ │ │ ├── rentals_clean.csv
│ │ │ └── pending_country_review.csv
│ │ │
│ │ └── 2026-02-28/
│ │ ├── customers_clean.csv
│ │ ├── rentals_clean.csv
│ │ ├── units_clean.csv
│ │ ├── pending_country_review.csv
│ │ └── unit_state_mismatches.csv
│ │
│ ├── manual/
│ │ ├── 2026-02-25/
│ │ │ ├── monthly_customer.csv
│ │ │ └── monthly_rentals.csv
│ │ └── 2026-02-28/
│ │ ├── monthly_customer.csv
│ │ └── monthly_rentals.csv
│ │
│ └── reference/
│ ├── city_aliases.csv
│ ├── countries.csv
│ └── spanish_provinces.csv
│
├── images/
│ └── data_model.png
│
├── sql/
│ ├── Diagram.mwb
│ ├── 2026-02-28 Queries.sql
│ ├── Checks_01_03_2026.sql
│ ├── Data_Quality_Checklist_Snapshot_2026-02-28.sql
│ ├── Monthly_check.sql
│ ├── Unit_rentals_checks.sql
│ └── Revisiones.sql
│
├── src/
│ ├── etl_units.py
│ ├── etl_customers.py
│ └── etl_rentals.py
│
├── notebooks/
├── .env
├── .gitignore
├── README_ES.md
└── README_EN.md


---

# 🗄 Data Model

Database: `storage_project`

### Implemented Core Tables

- `customers`
- `units`
- `unit_rentals`

---

### Entity-Relationship Diagram

![Data Model](images/data_model.png)

EER diagram designed in MySQL Workbench.  
Source file available at: `sql/Diagram.mwb`

---

## 🧠 Architectural Decisions

During early modeling, additional aggregation tables were considered:

- `bulk_areas`
- `bulk_occupancies`

After analyzing the operational system structure, it was determined that:

- All required information was already represented in:
  - `units`
  - `unit_rentals`

These tables were intentionally discarded to avoid unnecessary redundancy and keep the model fully normalized.

The final model prioritizes:

- Normalization
- Clear foreign key relationships
- Strict referential integrity

---

# 🔄 ETL Process

## ETL Pipeline Overview

The ETL pipeline is fully reproducible and idempotent.

Each execution processes a dated snapshot and performs:

1. Data extraction from raw CSV exports
2. Data cleaning and normalization
3. Data validation and anomaly detection
4. Loading into a relational MySQL database
5. Post-load integrity checks

### Extract
- Reads dated snapshot exports.

### Transform
- Cleaning and type casting
- Duplicate removal
- Geographic normalization
- Automatic inference of `country = Spain` when province is Spanish
- Export of inconsistency reports:
  - `pending_country_review.csv`
  - `unit_state_mismatches.csv`

### Load
- UPSERT into MySQL
- Post-load SQL validation checks

---

# 🛡 Data Quality Considerations

## 1️⃣ Snapshot Consistency

The ETL must be executed in this order:

1. `etl_units.py`
2. `etl_customers.py`
3. `etl_rentals.py`

Partial execution may temporarily generate cross-table inconsistencies.

---

## 2️⃣ Monthly Customers

In the operational system:

- Monthly units are marked as `blocked`.

In the analytical model:

- They are treated as `occupied`.

As of snapshot `2026-02-28`:

- 12 monthly units
- 1 additional blocked unit used for testing

---

## 3️⃣ Unit State vs Rental State Mismatches (4 cases)

Some units are marked as `available` while their latest rental still shows `occupied`.

Documented in:
  data/processed/2026-02-28/unit_state_mismatches.csv


No artificial corrections were applied in order to preserve source system integrity.

---

## 4️⃣ Missing Customer Location Data

Two active monthly customers are missing `city` and `province`.

- Data was not provided by clients.
- Values intentionally preserved as `NULL`.

---

# 🧹 Data Governance

- Complete removal of PII from public repository
- Versioned snapshots
- Referential integrity validation
- Documented inconsistencies
- Fully reproducible model

---

# 📊 Next Phase: Analytics & Visualization

The model is ready for:

- Occupancy analysis
- Vacancy time analysis
- Geographic segmentation
- Temporal evolution
- Customer behavior analysis

## Analytical Layer (SQL View for BI)

Beyond the ETL pipeline in Python, an analytical SQL view (`analytics_rentals`) was created in MySQL.

This view:
- Enriches rental data with unit and customer information
- Calculates rental duration dynamically
- Flags active rentals
- Identifies multi-unit customers
- Computes total m² occupied per customer

This view acts as a semantic layer for Tableau, allowing direct database connection instead of relying on exported CSV files.

This architecture separates:
- Raw data
- Cleaned data
- Analytical layer
- Visualization layer

It reflects a production-oriented data workflow.

Next step:

- Tableau dashboard development
- Corporate visual identity integration

---

# 🛠 Tech Stack

- MySQL
- Python
- pandas
- SQLAlchemy
- python-dotenv
- Tableau (analytical phase)
- Power BI (optional)

---

# 🚀 Current Status

✔ Relational model implemented  
✔ ETL fully operational  
✔ Snapshot automation  
✔ Data quality validated  
✔ Referential integrity confirmed  
✔ Ready for analytics phase  

Phase 1: Operational & occupancy analysis
Phase 2: Financial and revenue optimization analysis

---

## Tableau Dashboard

The analytical layer is visualized through interactive dashboards built in Tableau.

Main analyses include:

• Operational occupancy overview  
• Rental duration distribution  
• Customer geographic distribution  
• Customer nationality segmentation  

Tableau Public Dashboard:

[https://public.tableau.com/views/securistore_operational_dashboard/Cover?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link]