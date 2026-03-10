# 🗄️ Plataforma de Datos – Self-Storage

![Python](https://img.shields.io/badge/Python-Pipeline%20de%20Datos-blue)
![MySQL](https://img.shields.io/badge/MySQL-Base%20de%20Datos-orange)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-purple)
![ETL](https://img.shields.io/badge/ETL-Pipeline-green)
![Data Analytics](https://img.shields.io/badge/Data-Analytics-lightgrey)
![Estado](https://img.shields.io/badge/Proyecto-Completado-success)

Proyecto de **analítica de datos end-to-end** construido a partir de datos reales de una instalación de **self-storage**, transformando datos operativos en un sistema analítico para la toma de decisiones.

El proyecto incluye:

- Ingesta de datos operativos en bruto  
- Pipeline ETL en Python  
- Diseño de base de datos relacional en MySQL  
- Validación de calidad de datos  
- Capa analítica en SQL  
- Dashboards interactivos en Tableau  

El objetivo es convertir los datos operativos en **insights accionables** sobre:

- Ocupación y utilización de unidades  
- Comportamiento del cliente y duración de alquiler  
- Distribución geográfica de la demanda  
- Segmentación de clientes  

---

# 🎯 Objetivo del Proyecto

Este proyecto tiene dos objetivos complementarios.

## Propósito Académico

Proyecto final de un **bootcamp de Data Analytics**, enfocado en diseñar un sistema analítico completo a partir de datos operativos en bruto.

Objetivos de aprendizaje principales:

- Modelado relacional de bases de datos  
- Construcción de un pipeline ETL reproducible en Python  
- Implementación de validaciones de calidad de datos  
- Aplicación de buenas prácticas de gobernanza de datos y documentación  
- Desarrollo de un proyecto end-to-end para portfolio profesional  

---

## Caso de Negocio Real

El proyecto se desarrolló utilizando datos operativos de una instalación de **self-storage ubicada en Ondara (Alicante, España)**.

El objetivo es transformar los datos operativos en información útil para la toma de decisiones en áreas como:

- Ocupación y utilización de la instalación  
- Comportamiento y fidelización de clientes  
- Distribución geográfica de la demanda  
- Análisis de duración de alquiler  
- Rotación y vacancia de unidades  

⚠️ **Nota de privacidad**

Los datos publicados en este repositorio son **sintéticos y anonimizados**.  
Los datos operativos reales se procesan únicamente en un entorno local privado.

---

# 🏗 Arquitectura de Datos

El proyecto sigue una **arquitectura ETL por lotes basada en snapshots fechados** del sistema operativo.

Exportaciones CSV
↓
Pipeline ETL en Python
↓
Base de Datos Relacional MySQL
↓
Capa Analítica SQL
↓
Dashboards en Tableau


Principios de diseño:

- Reproducibilidad  
- Trazabilidad  
- Integridad referencial  
- Auditoría histórica de snapshots  

---

# 🔄 Pipeline ETL

El proceso ETL está implementado en Python y diseñado para ser **totalmente reproducible e idempotente**.

Cada ejecución procesa un snapshot fechado del sistema operativo.

---

## Extract (Extracción)

Los datos se exportan del sistema operativo en archivos CSV y se almacenan por fecha:

data/raw/YYY-MM-DD/


---

## Transform (Transformación)

La limpieza y transformación de datos se realiza con **pandas**.

Operaciones principales:

- Limpieza de datos y conversión de tipos
- Eliminación de duplicados
- Normalización geográfica
- Normalización de estados
- Validación de integridad referencial
- Validación estructural de datos

Las inconsistencias detectadas se exportan como reportes.

Ejemplos:

pending_country_revies.csv
unit_state_mismatches.csv


---

## Load (Carga)

Los datos limpios se cargan en MySQL mediante operaciones **UPSERT**:

INSERT ... ON DUPLICATE KEY UPDATE


Después de la carga se ejecutan consultas de validación para verificar:

- Integridad referencial  
- Consistencia entre tablas  
- Completitud de los datos  

---

# 📂 Estructura del Repositorio

El repositorio está organizado siguiendo un flujo típico de **ingeniería y analítica de datos**.

00_STORAGE_PROJECT/
│
├── data/
│ ├── raw/ # Snapshots originales del sistema operativo
│ ├── processed/ # Datos limpios generados por el ETL
│ ├── manual/ # Informes exportados manualmente
│ └── reference/ # Datos de referencia (países, provincias, alias)
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

# 🗄 Modelo de Datos

Base de datos: **storage_project**

Tablas principales implementadas:

- `customers`
- `units`
- `unit_rentals`

El modelo prioriza:

- Normalización
- Relaciones claras mediante claves foráneas
- Integridad referencial estricta

---

## Diagrama Entidad-Relación

![Data Model](docs/data_model.png)

El esquema de la base de datos fue diseñado en **MySQL Workbench**.

Archivo fuente disponible en:

sql/Diagram.mwb


---

# 🧠 Decisiones Arquitectónicas

Durante el modelado inicial se consideraron tablas adicionales de agregación:

- `bulk_areas`
- `bulk_occupancies`

Tras analizar la estructura del sistema operativo se determinó que toda la información necesaria ya estaba representada en:

- `units`
- `unit_rentals`

Estas tablas fueron descartadas para evitar:

- Redundancia
- Complejidad innecesaria
- Riesgo de inconsistencias

El modelo final prioriza **claridad, normalización y consistencia**.

---

# 🛡 Consideraciones de Calidad de Datos

Durante el desarrollo se identificaron varias situaciones relacionadas con la calidad de datos.

---

## Orden de ejecución del snapshot

El ETL debe ejecutarse en el siguiente orden:

1. `etl_units.py`
2. `etl_customers.py`
3. `etl_rentals.py`

Una ejecución parcial puede generar inconsistencias temporales entre tablas.

---

## Clientes Mensuales

En el sistema operativo:

Las unidades mensuales aparecen como **blocked**.

En el modelo analítico se consideran:

**unidades ocupadas**.

Snapshot `2026-02-28` incluye:

- 12 unidades mensuales
- 1 unidad bloqueada utilizada para pruebas

---

## Inconsistencias entre estado de unidad y alquiler

Algunas unidades aparecen como **available** mientras que el último alquiler sigue marcado como **occupied**.

Documentado en:

data/processed/2026-02-28/unit_state_mismatches.csv


No se aplicaron correcciones artificiales para preservar la integridad del sistema origen.

---

## Falta de información geográfica

Dos clientes activos no tienen información de ubicación (`city`, `province`).

Los valores se mantienen como **NULL** porque los datos no fueron proporcionados por los clientes.

---

# 📊 Capa Analítica

Se creó una vista SQL analítica llamada **analytics_rentals** para facilitar el consumo desde herramientas de BI.

Esta vista:

- Enriquecer los datos de alquiler con información de unidad y cliente
- Calcula la duración del alquiler dinámicamente
- Identifica alquileres activos
- Detecta clientes con múltiples unidades
- Calcula los metros cuadrados ocupados por cliente

Esta vista actúa como **capa semántica para Tableau**.

---

# 📈 Dashboards en Tableau

La capa analítica se visualiza mediante dashboards interactivos desarrollados en **Tableau**.

Principales análisis:

- Visión operativa de ocupación
- Distribución de duración de alquiler
- Distribución geográfica de clientes
- Segmentación por nacionalidad

Los workbooks se encuentran en:

tableau/ 

https://public.tableau.com/views/securistore_operational_dashboard/Cover?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

---

# 🛠 Stack Tecnológico

- Python  
- pandas  
- SQLAlchemy  
- python-dotenv  
- MySQL  
- Tableau  

Compatibilidad opcional con:

- Power BI

---

# 🚀 Estado del Proyecto

✔ Modelo relacional implementado  
✔ Pipeline ETL operativo  
✔ Arquitectura basada en snapshots  
✔ Validación de calidad de datos  
✔ Integridad referencial verificada  
✔ Capa analítica SQL implementada  
✔ Dashboards en Tableau desarrollados  

---

# 📌 Próximos Pasos

Posibles extensiones del proyecto:

- Análisis de optimización de precios y revenue  
- Predicción de tendencias de ocupación  
- Análisis de valor de vida del cliente (CLV)  
- Automatización del ETL  
- Integración en un data warehouse  

---

# 👤 Autor

**Matilde Cano Llinares**

Proyecto de Portfolio – Data Analytics  
Análisis Operativo y de Clientes en Self-Storage