# Data Dictionary — HMO Claims Risk & Financial Leakage Analytics Platform

## 1. Overview

This document describes the principal datasets, warehouse tables, and analytical fields used in the HMO Claims Risk & Financial Leakage Analytics Platform.

The project uses synthetic healthcare claims data to demonstrate data engineering, data quality validation, risk scoring, and financial analytics.

## 2. Source Data Entities

| Entity | Description |
|---|---|
| HMO | Health maintenance organizations included in the synthetic dataset. |
| Plan | Insurance plans associated with HMOs. |
| Member | Synthetic members enrolled in healthcare plans. |
| Provider | Healthcare providers submitting claims. |
| Diagnosis | Diagnosis records associated with healthcare services. |
| Service | Healthcare services billed on claims. |
| Date | Calendar dates used for time-based analysis. |
| Claims | Claim-level records containing submitted claim information. |
| Claim Lines | Individual service or procedure lines associated with claims. |
| Payments | Payment transactions associated with claims. |
| Authorizations | Authorization records used to assess whether required approvals exist. |
| Claim Risk | Risk scores, categories, and anomaly indicators associated with claims. |

## 3. SQL Server Database Structure

### Staging Schema (`stg`)

The staging schema stores imported source datasets before downstream analytical processing.

| Table | Purpose |
|---|---|
| `stg.Claims` | Staged claim records. |
| `stg.ClaimLines` | Staged claim-line records. |
| `stg.Payments` | Staged payment transactions. |
| `stg.Authorizations` | Staged authorization records. |
| `stg.HMO` | Staged HMO records. |
| `stg.Plan` | Staged insurance plan records. |
| `stg.Member` | Staged member records. |
| `stg.Provider` | Staged provider records. |
| `stg.Diagnosis` | Staged diagnosis records. |
| `stg.Service` | Staged service records. |
| `stg.Date` / `stg.Dates` | Date-related staging objects; confirm the exact object names and purposes in SQL Server. |
| `stg.Claim_Risk` | Staged claim risk scores and related indicators. |

### Data Warehouse Schema (`dw`)

The warehouse organizes data into dimensions and fact tables for analytical querying.

**Dimension tables**

| Table | Purpose |
|---|---|
| `dw.Dim_HMO` | HMO dimension. |
| `dw.Dim_Plan` | Insurance plan dimension. |
| `dw.Dim_Member` | Member dimension. |
| `dw.Dim_Provider` | Healthcare provider dimension. |
| `dw.Dim_Diagnosis` | Diagnosis dimension. |
| `dw.Dim_Service` | Healthcare service dimension. |
| `dw.Dim_Date` | Calendar date dimension. |

**Fact tables**

| Table | Purpose |
|---|---|
| `dw.Fact_Claims` | Claim-level analytical records. |
| `dw.Fact_Claim_Lines` | Claim-line-level analytical records. |
| `dw.Fact_Payments` | Payment transactions for financial analysis. |
| `dw.Fact_Authorizations` | Authorization records for claims analysis. |
| `dw.Fact_Claim_Risk` | Claim-level risk scores and categories. |

## 4. Reporting Views

The `rpt` schema provides analytical outputs for SQL exploration and downstream Power BI reporting.

| View | Intended use |
|---|---|
| `rpt.vw_Claim_Risk` | Analyze claims alongside their risk indicators. |
| `rpt.vw_High_Risk_Claims` | Review claims identified as high risk. |
| `rpt.vw_HMO_Risk` | Compare risk indicators across HMOs. |
| `rpt.vw_Member_Utilization` | Examine member healthcare utilization. |
| `rpt.vw_Payment_Leakage` | Investigate discrepancies between approved and paid amounts. |
| `rpt.vw_Provider_Risk` | Examine provider-related risk indicators. |
| `rpt.vw_Service_Cost_Anomalies` | Investigate unusual service-cost patterns. |

## 5. Risk Scoring

The Python risk-scoring process assigns points to selected indicators, including:

- High-value claims.
- Potential duplicate claims.
- Excessive member claim frequency.
- Suspicious claim timing.
- Provider anomalies.
- Service-cost anomalies.
- Excessive service quantities.
- Missing authorization.
- Plan coverage issues.

The configured categories are:

| Risk category | Configured score range |
|---|---:|
| Low | 0–3 |
| Medium | 4–6 |
| High | 7–10 |
| Critical | 11 and above |

These thresholds are specific to this project and are not presented as industry-standard thresholds.

## 6. Data Quality Considerations

Python validation and SQL checks are used to assess the generated data and warehouse relationships.

Some validation checks have identified differences between claim totals and claim-line totals, as well as potential plan-coverage inconsistencies. These require further investigation and should be considered when interpreting analytical results.

## 7. Important Interpretation Notes

- All records are synthetic and do not represent real patients, healthcare providers, or HMOs.
- A risk score indicates that a record may warrant review; it does not establish fraud.
- An approved-but-unpaid amount may represent an outstanding payment rather than a confirmed financial loss.
- Table descriptions are functional summaries. Exact column names, data types, and constraints should be verified against the database schema.