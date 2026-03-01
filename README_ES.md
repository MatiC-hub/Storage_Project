# 🗄️ Proyecto Personal – Base de Datos Almacén de Trasteros

## 🎯 Objetivo del Proyecto

Este proyecto tiene un doble objetivo:

### 1️⃣ Académico (Bootcamp & Portfolio)

Proyecto final de un bootcamp de Data Analytics cuyo objetivo es:

- Diseñar un modelo relacional completo desde cero.
- Implementar un pipeline ETL reproducible en Python.
- Aplicar buenas prácticas de modelado, integridad y gobernanza de datos.
- Construir un proyecto end-to-end profesional para portfolio.

### 2️⃣ Profesional (Caso real)

El proyecto se basa en un entorno empresarial real de gestión de trasteros.

Se ha diseñado una base de datos clara, mantenible y escalable que permite responder preguntas como:

- Distribución de clientes por país.
- Duración mínima, media y máxima de estancia.
- Ocupación actual y evolución temporal.
- Comportamiento de clientes activos y recientemente finalizados.

⚠️ **Nota de privacidad:**  
Los datos publicados en este repositorio son sintéticos.  
Los datos reales se procesan únicamente en entorno local privado.

---

## 🏗️ Arquitectura del Proyecto

### 📂 Estructura del Repositorio

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

## 🗄️ Modelo de Datos

Base de datos: `storage_project`

Tablas principales:

- `customers`
- `units`
- `rentals`
- `bulk_areas`
- `bulk_occupancies`

Separación clara entre:

- Entidades principales (clientes, espacios físicos)
- Eventos temporales (alquileres, ocupaciones)

El modelo está documentado mediante un EER diagram generado en MySQL Workbench.

---

## 🔄 Proceso ETL

El pipeline ETL está implementado en Python y es idempotente (re-ejecutable).

### Extract
- Lectura de CSV exportados desde el sistema externo.
- Organización por snapshots fechados.

### Transform
- Normalización de tipos y columnas.
- Eliminación de duplicados.
- Limpieza de valores inválidos.
- Estandarización geográfica:
  - Tabla `countries.csv`
  - Tabla `spanish_provinces.csv`
  - Tabla `city_aliases.csv`
- Autoasignación de `country = Spain` cuando la provincia es española.
- Export de registros pendientes de revisión (`pending_country_review.csv`).

### Load
- Inserción / Upsert en MySQL mediante `INSERT ... ON DUPLICATE KEY UPDATE`.
- Verificaciones de integridad posteriores.

---

## 🧹 Gobernanza y Calidad de Datos

El proyecto incluye:

- Eliminación completa de datos personales (PII) en el repositorio público.
- Validaciones de integridad:
  - Rentals sin unit.
  - Rentals sin customer.
- Reducción controlada de valores NULL.
- Snapshots versionados para trazabilidad y comparaciones temporales.

---

## 📊 Snapshots

Cada ejecución del ETL genera:

data/processed/<snapshot_date>/
customers_clean.csv
rentals_clean.csv
units_clean.csv
pending_country_review.csv


Esto permite:

- Reproducibilidad.
- Comparación entre fechas.
- Análisis de evolución.

---

## 🛠️ Stack Tecnológico

- MySQL
- Python
- pandas
- SQLAlchemy
- python-dotenv
- Power BI (próximo paso)
- Tableau (próximo paso)

---

## 🚀 Estado Actual

- Modelo relacional implementado.
- ETLs de customers, rentals y units operativos.
- Snapshots automatizados.
- Estandarización geográfica implementada.
- Base de datos validada sin PII.
- Listo para fase analítica.