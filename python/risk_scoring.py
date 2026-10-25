from pathlib import Path
import pandas as pd

# ============================================================
# HMO CLAIMS RISK ANALYTICS
# CLAIM RISK SCORING
# ============================================================
#
# Purpose:
# Convert the anomaly log into a claim-level risk score that can
# be used by SQL Server and Power BI for investigation and
# prioritization.
#
# IMPORTANT:
# These weights are synthetic project assumptions. They are not
# industry-standard fraud thresholds.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VALIDATED_DATA_DIR = PROJECT_ROOT / "Validated_Data"
OUTPUT_DIR = VALIDATED_DATA_DIR

CLAIMS_FILE = VALIDATED_DATA_DIR / "Fact_Claims.csv"
ANOMALY_FILE = VALIDATED_DATA_DIR / "Anomaly_Log.csv"

RISK_OUTPUT_FILE = OUTPUT_DIR / "Fact_Claim_Risk.csv"


# ============================================================
# RISK WEIGHTS
# ============================================================

RISK_WEIGHTS = {
    "High-Value Claim": 3,
    "Potential Duplicate Claim": 4,
    "Excessive Member Frequency": 3,
    "Suspicious Timing": 3,
    "Provider Risk": 3,
    "Service Cost Anomaly": 2,
    "Excessive Quantity": 2,
    "Missing Authorization": 3,
    "Plan Coverage Issue": 3,
}


# ============================================================
# RISK LEVELS
# ============================================================

def assign_risk_level(score):
    """
    Convert the final numerical risk score into a risk level.

    Project thresholds:
        0–3   = Low
        4–6   = Medium
        7–10  = High
        11+   = Critical
    """

    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    elif score <= 10:
        return "High"
    else:
        return "Critical"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    claims = pd.read_csv(CLAIMS_FILE)
    anomaly_log = pd.read_csv(ANOMALY_FILE)

    return claims, anomaly_log


# ============================================================
# PREPARE ANOMALY DATA
# ============================================================

def prepare_anomalies(anomaly_log):
    """
    Clean the anomaly log and prepare it for claim-level scoring.

    A claim can have multiple anomaly records of the same type
    because some anomaly types operate at claim-line level.

    For the risk score, each distinct anomaly type contributes
    its configured weight once per claim.

    This prevents a claim with several affected lines from
    receiving an artificially inflated score merely because it
    has more line-level records.
    """

    anomaly_log = anomaly_log.copy()

    required_columns = [
        "Claim_ID",
        "Anomaly_Type"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in anomaly_log.columns
    ]

    if missing_columns:
        raise ValueError(
            "Anomaly log is missing required columns: "
            + ", ".join(missing_columns)
        )

    anomaly_log = anomaly_log.dropna(
        subset=["Claim_ID", "Anomaly_Type"]
    ).copy()

    # Keep only recognized anomaly types.
    unknown_types = sorted(
        set(anomaly_log["Anomaly_Type"].unique())
        - set(RISK_WEIGHTS.keys())
    )

    if unknown_types:
        raise ValueError(
            "Unknown anomaly types found in Anomaly_Log.csv: "
            + ", ".join(unknown_types)
        )

    # One occurrence of each anomaly type per claim contributes
    # one risk weight.
    unique_anomalies = anomaly_log[
        ["Claim_ID", "Anomaly_Type"]
    ].drop_duplicates()

    unique_anomalies["Risk_Weight"] = (
        unique_anomalies["Anomaly_Type"]
        .map(RISK_WEIGHTS)
    )

    return anomaly_log, unique_anomalies


# ============================================================
# BUILD CLAIM RISK SCORE
# ============================================================

def build_claim_risk(claims, anomaly_log, unique_anomalies):

    # --------------------------------------------------------
    # Start with every claim.
    # This ensures claims with no anomalies receive score 0.
    # --------------------------------------------------------

    risk = claims[
        [
            "Claim_ID",
            "Member_ID",
            "Provider_ID",
            "Plan_ID",
            "Claim_Date",
            "Claim_Amount",
            "Approved_Amount",
            "Rejected_Amount",
        ]
    ].copy()

    # --------------------------------------------------------
    # Calculate numerical risk score
    # --------------------------------------------------------

    score_by_claim = (
        unique_anomalies
        .groupby("Claim_ID", as_index=False)["Risk_Weight"]
        .sum()
        .rename(columns={"Risk_Weight": "Risk_Score"})
    )

    risk = risk.merge(
        score_by_claim,
        on="Claim_ID",
        how="left"
    )

    risk["Risk_Score"] = (
        pd.to_numeric(risk["Risk_Score"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    risk["Risk_Level"] = risk["Risk_Score"].apply(
        assign_risk_level
    )

    # --------------------------------------------------------
    # Anomaly count
    #
    # This is the actual number of anomaly records, while the
    # score is based on distinct anomaly types per claim.
    # --------------------------------------------------------

    anomaly_count = (
        anomaly_log
        .groupby("Claim_ID")
        .size()
        .reset_index(name="Anomaly_Record_Count")
    )

    risk = risk.merge(
        anomaly_count,
        on="Claim_ID",
        how="left"
    )

    risk["Anomaly_Record_Count"] = (
        risk["Anomaly_Record_Count"]
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Distinct anomaly type count
    # --------------------------------------------------------

    anomaly_type_count = (
        unique_anomalies
        .groupby("Claim_ID")
        .size()
        .reset_index(name="Distinct_Anomaly_Type_Count")
    )

    risk = risk.merge(
        anomaly_type_count,
        on="Claim_ID",
        how="left"
    )

    risk["Distinct_Anomaly_Type_Count"] = (
        risk["Distinct_Anomaly_Type_Count"]
        .fillna(0)
        .astype(int)
    )

    return risk


# ============================================================
# ADD RISK FLAGS
# ============================================================

def add_risk_flags(risk, unique_anomalies):
    """
    Add one binary flag for every anomaly type.

    These flags make downstream SQL and Power BI analysis much
    easier than parsing a text field.
    """

    flag_map = {
        "High-Value Claim": "High_Value_Flag",
        "Potential Duplicate Claim": "Duplicate_Flag",
        "Excessive Member Frequency": "Frequency_Flag",
        "Suspicious Timing": "Suspicious_Timing_Flag",
        "Provider Risk": "Provider_Risk_Flag",
        "Service Cost Anomaly": "Service_Cost_Anomaly_Flag",
        "Excessive Quantity": "Excessive_Quantity_Flag",
        "Missing Authorization": "Missing_Authorization_Flag",
        "Plan Coverage Issue": "Plan_Coverage_Flag",
    }

    for anomaly_type, flag_column in flag_map.items():

        affected_claims = set(
            unique_anomalies.loc[
                unique_anomalies["Anomaly_Type"] == anomaly_type,
                "Claim_ID"
            ]
        )

        risk[flag_column] = (
            risk["Claim_ID"]
            .isin(affected_claims)
            .astype(int)
        )

    return risk


# ============================================================
# ADD RISK DRIVER SUMMARY
# ============================================================

def add_risk_driver_summary(risk, unique_anomalies):

    drivers = (
        unique_anomalies
        .groupby("Claim_ID")["Anomaly_Type"]
        .apply(lambda values: " | ".join(sorted(set(values))))
        .reset_index(name="Risk_Drivers")
    )

    risk = risk.merge(
        drivers,
        on="Claim_ID",
        how="left"
    )

    risk["Risk_Drivers"] = (
        risk["Risk_Drivers"]
        .fillna("None")
    )

    return risk


# ============================================================
# VALIDATE RISK SCORES
# ============================================================

def validate_risk_scores(risk, unique_anomalies):

    expected_scores = (
        unique_anomalies
        .groupby("Claim_ID")["Risk_Weight"]
        .sum()
    )

    scored_claims = risk.set_index("Claim_ID")["Risk_Score"]

    mismatches = []

    for claim_id, expected_score in expected_scores.items():

        actual_score = scored_claims.get(claim_id, None)

        if actual_score != int(expected_score):
            mismatches.append(
                (
                    claim_id,
                    int(expected_score),
                    actual_score
                )
            )

    if mismatches:
        print(
            f"[FAIL] Risk score validation: "
            f"{len(mismatches):,} mismatched claims."
        )

        for claim_id, expected, actual in mismatches[:10]:
            print(
                f"  {claim_id}: expected {expected}, "
                f"found {actual}"
            )

        raise ValueError(
            "Risk score validation failed."
        )

    print(
        "[PASS] Risk score validation: "
        "All scored claims match their anomaly weights."
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(risk, unique_anomalies):

    print("\n" + "=" * 60)
    print("RISK SCORING SUMMARY")
    print("=" * 60)

    print(
        f"Total claims scored: "
        f"{len(risk):,}"
    )

    print(
        f"Claims with at least one anomaly: "
        f"{(risk['Risk_Score'] > 0).sum():,}"
    )

    print(
        f"Claims with no anomaly: "
        f"{(risk['Risk_Score'] == 0).sum():,}"
    )

    print("\nRisk level distribution:")

    level_order = [
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    level_counts = (
        risk["Risk_Level"]
        .value_counts()
        .reindex(level_order, fill_value=0)
    )

    for level, count in level_counts.items():
        print(f"  {level}: {count:,}")

    print("\nRisk score distribution:")

    print(
        risk["Risk_Score"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nTop 10 highest-risk claims:")

    top_claims = risk[
        [
            "Claim_ID",
            "Risk_Score",
            "Risk_Level",
            "Anomaly_Record_Count",
            "Distinct_Anomaly_Type_Count",
            "Risk_Drivers",
        ]
    ].sort_values(
        ["Risk_Score", "Anomaly_Record_Count"],
        ascending=[False, False]
    ).head(10)

    print(top_claims.to_string(index=False))


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_risk_data(risk):

    risk.to_csv(
        RISK_OUTPUT_FILE,
        index=False
    )

    print(
        "\nRisk scoring output saved successfully."
    )

    print(
        f"Output file: {RISK_OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("HMO CLAIMS RISK ANALYTICS")
    print("CLAIM RISK SCORING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    print("\nLoading validated data...")

    claims, anomaly_log = load_data()

    print(
        f"Claims loaded: "
        f"{len(claims):,}"
    )

    print(
        f"Anomaly records loaded: "
        f"{len(anomaly_log):,}"
    )

    # --------------------------------------------------------
    # Prepare anomalies
    # --------------------------------------------------------

    anomaly_log, unique_anomalies = prepare_anomalies(
        anomaly_log
    )

    print(
        f"Distinct claim/anomaly-type combinations: "
        f"{len(unique_anomalies):,}"
    )

    # --------------------------------------------------------
    # Build score
    # --------------------------------------------------------

    risk = build_claim_risk(
        claims,
        anomaly_log,
        unique_anomalies
    )

    # --------------------------------------------------------
    # Add flags
    # --------------------------------------------------------

    risk = add_risk_flags(
        risk,
        unique_anomalies
    )

    # --------------------------------------------------------
    # Add driver summary
    # --------------------------------------------------------

    risk = add_risk_driver_summary(
        risk,
        unique_anomalies
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_risk_scores(
        risk,
        unique_anomalies
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_risk_data(risk)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_summary(
        risk,
        unique_anomalies
    )

    print("\nRisk scoring completed successfully.")


if __name__ == "__main__":
    main()
