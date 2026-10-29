# HMO Claims Risk & Financial Leakage Analytics Platform

## 1. Project Overview

The HMO Claims Risk & Financial Leakage Analytics Platform is an end-to-end healthcare analytics project designed to analyze synthetic health insurance claims data, identify potential anomalies, assess claims risk, and investigate payment discrepancies.

The project combines Python for data generation and risk scoring, SQL Server for data storage and analytical querying, and Power BI for business intelligence reporting.

**Important:** The dataset is synthetic. Risk indicators highlight records requiring further investigation; they do not establish confirmed fraud or actual financial loss.

## 2. System Architecture

The project follows this workflow:

**Python Data Generation → Anomaly Injection and Risk Scoring → SQL Server Staging → Data Warehouse → Reporting Views → Power BI**

### Layer 1: Data Generation and Processing

Python scripts generate synthetic healthcare claims data and related records.

Key components include:

- `config.py`: Project configuration.
- `generator.py`: Synthetic data generation.
- `anomaly_injector.py`: Injection of selected anomalies into the synthetic dataset.
- `risk_scoring.py`: Assignment of risk scores based on configured rules.
- `validation.py`: Data validation checks.

### Layer 2: SQL Server Staging

The staging layer uses the `stg` schema to hold incoming datasets before analytical processing.

Staging tables cover entities such as claims, claim lines, payments, authorizations, HMOs, plans, members, providers, diagnoses, services, dates, and claim risk records.

### Layer 3: Data Warehouse

The `dw` schema organizes data into dimension and fact tables to support consistent analytical queries.

**Dimension tables**
- `Dim_HMO`
- `Dim_Plan`
- `Dim_Member`
- `Dim_Provider`
- `Dim_Diagnosis`
- `Dim_Service`
- `Dim_Date`

**Fact tables**
- `Fact_Claims`
- `Fact_Claim_Lines`
- `Fact_Payments`
- `Fact_Authorizations`
- `Fact_Claim_Risk`

This structure supports analysis across claims, members, providers, HMOs, services, dates, and payments.

### Layer 4: Reporting and Analytics

The `rpt` schema contains reporting views that provide analytical outputs for downstream reporting.

The views cover:

- Overall claims risk.
- High-risk claims requiring review.
- Risk comparisons across HMOs.
- Member utilization.
- Payment discrepancies.
- Provider risk indicators.
- Service cost anomalies.

SQL validation and analysis scripts support quality checks and further investigation.

### Layer 5: Business Intelligence

Power BI will consume the analytical outputs to present interactive dashboards, performance indicators, and business insights.

The reporting layer is intended to help users prioritize claims for review, investigate unusual utilization and service costs, compare HMO risk patterns, and understand differences between approved and paid amounts.

## 3. Data Quality and Risk Methodology

The project includes Python validation and SQL quality checks.

Configured risk rules assign points to selected indicators, including high-value claims, potential duplicates, excessive frequency, suspicious timing, provider anomalies, unusual service costs, excessive quantities, missing authorization, and plan coverage issues.

Risk categories are assigned using the project's configured score thresholds. These thresholds are project-specific analytical assumptions and should not be interpreted as industry standards.

## 4. Technology Stack

- **Python:** Synthetic data generation, anomaly injection, risk scoring, and validation.
- **SQL Server:** Staging, dimensional warehouse, reporting views, and analytical queries.
- **Power BI:** Planned dashboarding and business intelligence reporting.
- **GitHub:** Version control, documentation, and collaborative development.

## 5. Limitations

- The dataset is synthetic and does not represent real patients, providers, or HMO operations.
- Anomaly indicators are intended for investigation, not as proof of fraud.
- Approved-but-unpaid amounts may represent outstanding payments rather than financial losses.
- Results depend on the assumptions and quality of the generated data.
- Business conclusions should be interpreted within the context of the project's synthetic dataset.

## 6. Intended Outcome

The project demonstrates an end-to-end healthcare analytics workflow combining Python, SQL Server, data quality checks, risk analysis, and business intelligence reporting.