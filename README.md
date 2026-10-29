# HMO Claims Risk & Financial Leakage Analytics Platform

An end-to-end healthcare analytics project using Python, SQL Server, and Power BI to investigate synthetic health insurance claims, identify potential risk indicators, and analyze payment discrepancies.

## Project Overview

Health insurance claims operations involve large volumes of claims, service records, authorization data, and payment transactions. Analyzing these records can help identify unusual patterns and prioritize claims for further investigation.

This project demonstrates a healthcare analytics workflow that combines synthetic data generation, anomaly injection, risk scoring, data validation, SQL Server data warehousing, and business intelligence reporting.

**Important:** All data is synthetic. Risk indicators do not establish confirmed fraud, and approved-but-unpaid amounts do not automatically represent financial losses.

## Project Objectives

- Generate synthetic healthcare claims and related datasets.
- Introduce controlled anomalies for analytical testing.
- Apply configurable rules to score claim risk.
- Validate data quality and document inconsistencies.
- Store and organize datasets in SQL Server.
- Build reporting views for claims, payments, members, providers, and HMOs.
- Prepare analytical outputs for Power BI dashboards.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation, anomaly injection, risk scoring, and validation |
| SQL Server | Staging, warehouse storage, reporting views, and analysis |
| Power BI | Business intelligence and dashboard reporting |
| GitHub | Version control, project documentation, and collaboration |

## Architecture

The project follows this workflow:

**Python Data Generation → Anomaly Injection → Risk Scoring and Validation → SQL Server Staging → Data Warehouse → Reporting Views → Power BI**

See [`docs/architecture.md`](docs/architecture.md) for the system architecture.

## Dataset Overview

The current SQL Server dataset includes:

| Dataset | Records |
|---|---:|
| Claims | 101,500 |
| Claim lines | 248,547 |
| Payments | 72,239 |
| Authorizations | 54,787 |
| Members | 10,000 |
| Providers | 120 |
| HMOs | 5 |
| Plans | 20 |

These figures describe the generated dataset and recorded SQL Server table counts.

## SQL Server Design

The database uses three principal schemas:

- **`stg`** — staging tables for imported datasets.
- **`dw`** — warehouse dimensions and fact tables.
- **`rpt`** — reporting views for downstream analysis.

The reporting layer supports analysis of:

- Claims risk.
- High-risk claims.
- HMO risk indicators.
- Member utilization.
- Payment discrepancies.
- Provider risk indicators.
- Service-cost anomalies.

SQL scripts are available in the [`sql`](sql/) directory.

## Python Components

The [`python`](python/) directory contains the main processing scripts:

- `config.py` — project configuration.
- `generator.py` — synthetic dataset generation.
- `anomaly_injector.py` — controlled anomaly injection.
- `risk_scoring.py` — configurable claims risk scoring.
- `validation.py` — data validation checks.

## Data Quality

The implemented Python validation suite reported:

- 78 passed checks.
- 2 warnings.
- 0 failed checks.

Outstanding warnings include claim-to-line reconciliation differences and potential plan-coverage inconsistencies. These findings require further investigation.

See [`docs/data_quality_report.md`](docs/data_quality_report.md) for details.

The data dictionary is available in [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Analytical Findings and Interpretation

The risk-scoring process categorizes claims according to configured rules. These categories help prioritize records for investigation within the synthetic dataset.

The analysis also examines differences between approved and paid amounts. Such differences may represent outstanding payments or other timing and processing issues; they should not automatically be classified as financial losses.

Results depend on the synthetic data, configured scoring rules, and validation assumptions.

## Project Structure

```text
HMO-claims-risk-analytics/
├── python/
│   ├── config.py
│   ├── generator.py
│   ├── anomaly_injector.py
│   ├── risk_scoring.py
│   └── validation.py
├── sql/
│   ├── HMO_Claims_Risk_Analytics_Schema.sql
│   ├── HMO_Claims_Reporting_Views.sql
│   ├── 01_Validation/
│   └── 02_Analysis/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── data_quality_report.md
├── powerbi/
├── reports/
├── data/
└── README.md
```

## Limitations

- The data is synthetic and does not represent real patients, providers, or HMOs.
- Risk scores are rule-based indicators, not proof of fraud.
- Claim-to-line reconciliation and plan-coverage warnings remain unresolved.
- Financial discrepancies require further investigation before they can be classified as losses.
- Results should be interpreted as a demonstration of analytics methods, not as actual healthcare industry findings.

## Intended Audience

This project demonstrates practical skills relevant to data analyst, business intelligence, healthcare analytics, and data engineering roles.

It is also designed to support collaboration between SQL/data engineering and Power BI development.

## Future Improvements

- Investigate outstanding data-quality warnings.
- Expand SQL integrity and reconciliation checks.
- Standardize risk category definitions across SQL and Power BI.
- Develop interactive Power BI dashboards and documented DAX measures.
- Add reproducible setup and execution instructions.

## Disclaimer

This is a portfolio project built with synthetic data for educational and demonstration purposes. It is not intended for clinical decision-making, actual claims adjudication, or the determination of insurance fraud.
