# 🗄️ Self-Storage Facility Data Platform

![Python](https://img.shields.io/badge/Python-Data%20Pipeline-blue)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-purple)
![ETL](https://img.shields.io/badge/ETL-Pipeline-green)
![Data Analytics](https://img.shields.io/badge/Data-Analytics-lightgrey)
![Status](https://img.shields.io/badge/Project-Completed-success)

End-to-end data analytics project built around a real **self-storage facility**, transforming operational data into an analytical system for decision-making.

The project includes:

- Raw operational data ingestion
- Python ETL pipeline
- Relational database design in MySQL
- Data quality validation
- Analytical SQL layer
- Interactive dashboards in Tableau

The goal is to convert operational data into **actionable business insights** about:

- Occupancy and unit utilization  
- Customer behaviour and rental duration  
- Geographic distribution of demand  
- Customer segmentation  

---

# 🎯 Project Objective

This project has two complementary goals.

## Academic Purpose

Final project of a **Data Analytics Bootcamp**, focused on designing a complete analytical system from raw operational data.

Key learning objectives include:

- Relational database modeling
- Building a reproducible ETL pipeline in Python
- Implementing data quality validation
- Applying best practices in data governance and documentation
- Creating an end-to-end portfolio project

---

## Real Business Case

The project was developed using operational data from a **self-storage facility located in Ondara (Alicante, Spain)**.

The objective is to transform operational data into insights that support decision-making in areas such as:

- Facility occupancy and utilization
- Customer behaviour and retention
- Geographic demand distribution
- Rental duration analysis
- Unit turnover and vacancy analysis

⚠️ **Privacy Note**

The data published in this repository is **synthetic and anonymized**.  
Real operational data is processed only in a private local environment.

---

# 🏗 Data Architecture

The project follows a **batch ETL architecture based on dated operational snapshots**.

Raw CSV Exports
↓
Python ETL Pipeline
↓
MySQL Relational Database
↓
SQL Analytical Layer
↓
Tableau Dashboards


Key design principles:

- Reproducibility  
- Traceability  
- Referential integrity  
- Historical snapshot auditing  

---

# 🔄 ETL Pipeline

The ETL process is implemented in Python and designed to be **fully reproducible and idempotent**.

Each execution processes a dated snapshot of the operational system.

## Extract

Raw data is exported from the operational system as CSV files and stored by date:


Key design principles:

- Reproducibility  
- Traceability  
- Referential integrity  
- Historical snapshot auditing  

---

# 🔄 ETL Pipeline

The ETL process is implemented in Python and designed to be **fully reproducible and idempotent**.

Each execution processes a dated snapshot of the operational system.

## Extract

Raw data is exported from the operational system as CSV files and stored by date:


Key design principles:

- Reproducibility  
- Traceability  
- Referential integrity  
- Historical snapshot auditing  

---

# 🔄 ETL Pipeline

The ETL process is implemented in Python and designed to be **fully reproducible and idempotent**.

Each execution processes a dated snapshot of the operational system.

## Extract

Raw data is exported from the operational system as CSV files and stored by date:


Key design principles:

- Reproducibility  
- Traceability  
- Referential integrity  
- Historical snapshot auditing  

---

# 🔄 ETL Pipeline

The ETL process is implemented in Python and designed to be **fully reproducible and idempotent**.

Each execution processes a dated snapshot of the operational system.

## Extract

Raw data is exported from the operational system as CSV files and stored by date:

data/raw/YYYY-MM-DD/


---

## Transform

Cleaning and transformation is performed using **pandas**.

Main operations include:

- Data cleaning and type casting
- Duplicate removal
- Geographic normalization
- State normalization
- Referential integrity validation
- Structural validation

Inconsistencies detected during the transformation stage are exported as reports.

Examples:


---

## Transform

Cleaning and transformation is performed using **pandas**.

Main operations include:

- Data cleaning and type casting
- Duplicate removal
- Geographic normalization
- State normalization
- Referential integrity validation
- Structural validation

Inconsistencies detected during the transformation stage are exported as reports.

Examples:

---

## Transform

Cleaning and transformation is performed using **pandas**.

Main operations include:

- Data cleaning and type casting
- Duplicate removal
- Geographic normalization
- State normalization
- Referential integrity validation
- Structural validation

Inconsistencies detected during the transformation stage are exported as reports.

Examples:

pending_country_review.csv
unit_state_mismatches.csv


---

## Load

Cleaned data is loaded into MySQL using **UPSERT operations**:


---

## Load

Cleaned data is loaded into MySQL using **UPSERT operations**:

INSERT ... ON DUPLICATE KEY UPDATE


After loading, SQL validation queries confirm:

- Referential integrity
- Cross-table consistency
- Data completeness

---

# 📂 Repository Structure

The repository is organized following a typical **data engineering and analytics workflow**.

00_STORAGE_PROJECT/
│
├── data/
│ ├── raw/ # Original operational snapshots
│ ├── processed/ # Cleaned data produced by the ETL
│ ├── manual/ # Manually exported operational reports
│ └── reference/ # Reference datasets (countries, provinces, aliases)
│
├── docs/
│ ├── Analisis-Operativo-y-de-Clientes-Self-Storage.pdf
│ ├── current_snapshot.md
│ └── data_model.png
│
├── sql/
│ ├── Diagram.mwb
│ ├── Analytics_rentals_for_Tableau.sql
│ ├── Data_Quality_Checklist_Snapshot_2026-02-28.sql
│ ├── Checks_01_03_2026.sql
│ ├── Monthly_check.sql
│ ├── Unit_rentals_checks.sql
│ └── Reviews.sql
│
├── src/
│ ├── etl_units.py
│ ├── etl_customers.py
│ └── etl_rentals.py
│
├── tableau/
│ ├── securistore_final_presentation.twbx
│ └── securistore_workbook.twbx
│
├── .env
├── .gitignore
├── README_EN.md
└── README_ES.md


---

# 🗄 Data Model

Database: **storage_project**

Core tables:

- `customers`
- `units`
- `unit_rentals`

The model prioritizes:

- Normalization
- Clear foreign key relationships
- Strict referential integrity

---

## Entity Relationship Diagram

![Data Model](docs/data_model.png)

The database schema was designed using **MySQL Workbench**.

Source file available in:


---

# 🗄 Data Model

Database: **storage_project**

Core tables:

- `customers`
- `units`
- `unit_rentals`

The model prioritizes:

- Normalization
- Clear foreign key relationships
- Strict referential integrity

---

## Entity Relationship Diagram

![Data Model](docs/data_model.png)

The database schema was designed using **MySQL Workbench**.

Source file available in:

spl/Diagram.mwb


---

# 🧠 Architectural Decisions

During early modeling, additional aggregation tables were considered:

- `bulk_areas`
- `bulk_occupancies`

After analyzing the operational system structure it was determined that all necessary information already existed within:

- `units`
- `unit_rentals`

These tables were intentionally discarded to avoid:

- Redundancy
- Unnecessary complexity
- Risk of inconsistencies

The final model prioritizes **clarity, normalization and consistency**.

---

# 🛡 Data Quality Considerations

Several data quality situations were identified during development.

## Snapshot Execution Order

The ETL should be executed in the following order:

1. `etl_units.py`
2. `etl_customers.py`
3. `etl_rentals.py`

Partial execution may temporarily generate cross-table inconsistencies.

---

## Monthly Customers

In the operational system:

Monthly units are marked as **blocked**.

In the analytical model they are treated as:

**occupied units**.

Snapshot `2026-02-28` includes:

- 12 monthly units
- 1 blocked unit used for testing

---

## Unit State vs Rental State Mismatches

Some units appear as **available** while the latest rental still indicates **occupied**.

Documented in:

data/processed/2026-02-28/uniy_state_mismatches.csv


No artificial corrections were applied to preserve source system integrity.

---

## Missing Customer Location Data

Two active customers are missing geographic information (`city`, `province`).

The values remain **NULL** because the data was not provided by the clients.

---

# 📊 Analytical Layer

An analytical SQL view named **`analytics_rentals`** was created to simplify BI consumption.

This view:

- Enriches rental data with unit and customer attributes
- Calculates rental duration dynamically
- Flags active rentals
- Identifies multi-unit customers
- Calculates total occupied square meters per customer

This view acts as the **semantic layer for Tableau dashboards**.

---

# 📈 Tableau Dashboard

The analytical layer is visualized through interactive dashboards built in **Tableau**.

Main analyses include:

- Operational occupancy overview
- Rental duration distribution
- Customer geographic distribution
- Customer nationality segmentation

Tableau workbooks available in:

tablleau/

https://public.tableau.com/views/securistore_operational_dashboard/Cover?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

---

# 🛠 Tech Stack

- Python
- pandas
- SQLAlchemy
- python-dotenv
- MySQL
- Tableau

Optional BI compatibility:

- Power BI

---

# 🚀 Project Status

✔ Relational database model implemented  
✔ ETL pipeline fully operational  
✔ Snapshot-based architecture  
✔ Data quality validation implemented  
✔ Referential integrity verified  
✔ Analytical SQL layer implemented  
✔ Tableau dashboards developed  

---

# 📌 Next Steps

Potential future extensions include:

- Revenue and pricing optimization analysis
- Forecasting occupancy trends
- Customer lifetime value analysis
- Automated ETL scheduling
- Data warehouse integration

---

# 👤 Author

**Matilde Cano Llinares**

Data Analytics Portfolio Project  
Self-Storage Operational & Customer Analysis