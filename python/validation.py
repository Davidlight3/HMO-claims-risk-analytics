import pandas as pd

from config import (
    RAW_DATA_DIR,
    VALIDATED_DATA_DIR
)


# ============================================================
# VALIDATION COUNTERS
# ============================================================

PASS_COUNT = 0
WARNING_COUNT = 0
FAIL_COUNT = 0


def record_result(
    test_name,
    passed,
    message,
    severity="FAIL"
):
    """
    Record and display the result of a validation test.
    """

    global PASS_COUNT
    global WARNING_COUNT
    global FAIL_COUNT

    if passed:

        PASS_COUNT += 1

        print(
            f"[PASS] {test_name}: {message}"
        )

    elif severity == "WARNING":

        WARNING_COUNT += 1

        print(
            f"[WARNING] {test_name}: {message}"
        )

    else:

        FAIL_COUNT += 1

        print(
            f"[FAIL] {test_name}: {message}"
        )


# ============================================================
# LOAD DIMENSION DATA
# ============================================================

def load_dimension_data():

    hmo_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_HMO.csv"
    )

    plan_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_Plan.csv"
    )

    member_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_Member.csv"
    )

    provider_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_Provider.csv"
    )

    diagnosis_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_Diagnosis.csv"
    )

    service_df = pd.read_csv(
        RAW_DATA_DIR / "Dim_Service.csv"
    )

    return (
        hmo_df,
        plan_df,
        member_df,
        provider_df,
        diagnosis_df,
        service_df
    )


# ============================================================
# LOAD VALIDATED FACT DATA
# ============================================================

def load_fact_data():

    claims = pd.read_csv(
        VALIDATED_DATA_DIR / "Fact_Claims.csv"
    )

    claim_lines = pd.read_csv(
        VALIDATED_DATA_DIR / "Fact_Claim_Lines.csv"
    )

    payments = pd.read_csv(
        VALIDATED_DATA_DIR / "Fact_Payments.csv"
    )

    authorizations = pd.read_csv(
        VALIDATED_DATA_DIR / "Fact_Authorizations.csv"
    )

    anomaly_log = pd.read_csv(
        VALIDATED_DATA_DIR / "Anomaly_Log.csv"
    )

    return (
        claims,
        claim_lines,
        payments,
        authorizations,
        anomaly_log
    )


# ============================================================
# 1. DIMENSION RECORD COUNT CHECK
# ============================================================

def check_dimension_record_counts(
    hmo_df,
    plan_df,
    member_df,
    provider_df,
    diagnosis_df,
    service_df
):

    print()
    print("=" * 60)
    print("1. DIMENSION RECORD COUNT CHECK")
    print("=" * 60)

    expected_counts = {
        "HMOs": (hmo_df, 5),
        "Plans": (plan_df, 20),
        "Members": (member_df, 10_000),
        "Providers": (provider_df, 120),
        "Diagnoses": (diagnosis_df, 35),
        "Services": (service_df, 30)
    }

    for name, (
        dataframe,
        expected
    ) in expected_counts.items():

        actual = len(dataframe)

        record_result(
            f"{name} count",
            actual == expected,
            f"Expected {expected:,}; found {actual:,}."
        )


# ============================================================
# 2. DIMENSION DUPLICATE ID CHECK
# ============================================================

def check_dimension_duplicate_ids(
    hmo_df,
    plan_df,
    member_df,
    provider_df,
    diagnosis_df,
    service_df
):

    print()
    print("=" * 60)
    print("2. DIMENSION DUPLICATE ID CHECK")
    print("=" * 60)

    id_checks = {
        "HMO_ID": hmo_df,
        "Plan_ID": plan_df,
        "Member_ID": member_df,
        "Provider_ID": provider_df,
        "Diagnosis_ID": diagnosis_df,
        "Service_ID": service_df
    }

    for column, dataframe in id_checks.items():

        duplicates = (
            dataframe[column]
            .duplicated()
            .sum()
        )

        record_result(
            f"{column} uniqueness",
            duplicates == 0,
            f"Duplicate values: {duplicates:,}."
        )


# ============================================================
# 3. HMO / PLAN / MEMBER RELATIONSHIPS
# ============================================================

def check_hmo_plan_member_relationships(
    hmo_df,
    plan_df,
    member_df
):

    print()
    print("=" * 60)
    print("3. HMO / PLAN / MEMBER RELATIONSHIPS")
    print("=" * 60)

    valid_hmos = set(
        hmo_df["HMO_ID"]
    )

    valid_plans = set(
        plan_df["Plan_ID"]
    )

    invalid_plan_hmos = (
        ~plan_df["HMO_ID"].isin(valid_hmos)
    ).sum()

    invalid_member_hmos = (
        ~member_df["HMO_ID"].isin(valid_hmos)
    ).sum()

    invalid_member_plans = (
        ~member_df["Plan_ID"].isin(valid_plans)
    ).sum()

    record_result(
        "Plans → HMOs",
        invalid_plan_hmos == 0,
        f"Invalid HMO references: {invalid_plan_hmos:,}."
    )

    record_result(
        "Members → HMOs",
        invalid_member_hmos == 0,
        f"Invalid HMO references: {invalid_member_hmos:,}."
    )

    record_result(
        "Members → Plans",
        invalid_member_plans == 0,
        f"Invalid Plan references: {invalid_member_plans:,}."
    )

    plan_hmo_map = (
        plan_df
        .set_index("Plan_ID")["HMO_ID"]
        .to_dict()
    )

    expected_hmo = member_df["Plan_ID"].map(
        plan_hmo_map
    )

    mismatches = (
        member_df["HMO_ID"]
        != expected_hmo
    ).sum()

    record_result(
        "Member Plan/HMO consistency",
        mismatches == 0,
        f"Mismatched Member → Plan → HMO relationships: {mismatches:,}."
    )


# ============================================================
# 4. MEMBER QUALITY CHECKS
# ============================================================

def get_expected_age_group(age):

    if age <= 17:
        return "0-17"

    if age <= 30:
        return "18-30"

    if age <= 45:
        return "31-45"

    if age <= 60:
        return "46-60"

    return "61+"


def check_member_quality(member_df):

    print()
    print("=" * 60)
    print("4. MEMBER QUALITY CHECKS")
    print("=" * 60)

    valid_genders = {
        "Male",
        "Female"
    }

    invalid_gender = (
        ~member_df["Gender"].isin(valid_genders)
    ).sum()

    record_result(
        "Gender values",
        invalid_gender == 0,
        f"Invalid gender values: {invalid_gender:,}."
    )

    valid_statuses = {
        "Active",
        "Inactive"
    }

    invalid_status = (
        ~member_df["Member_Status"].isin(valid_statuses)
    ).sum()

    record_result(
        "Member status values",
        invalid_status == 0,
        f"Invalid member status values: {invalid_status:,}."
    )

    expected_groups = member_df["Age"].apply(
        get_expected_age_group
    )

    age_group_mismatches = (
        member_df["Age_Group"]
        != expected_groups
    ).sum()

    record_result(
        "Age group consistency",
        age_group_mismatches == 0,
        f"Age group mismatches: {age_group_mismatches:,}."
    )


# ============================================================
# 5. MEMBER DATE VALIDATION
# ============================================================

def check_member_dates(member_df):

    print()
    print("=" * 60)
    print("5. MEMBER DATE VALIDATION")
    print("=" * 60)

    df = member_df.copy()

    df["Date_of_Birth"] = pd.to_datetime(
        df["Date_of_Birth"],
        errors="coerce"
    )

    df["Enrollment_Date"] = pd.to_datetime(
        df["Enrollment_Date"],
        errors="coerce"
    )

    df["Termination_Date"] = pd.to_datetime(
        df["Termination_Date"],
        errors="coerce"
    )

    invalid_dates = (
        df["Date_of_Birth"].isna()
        | df["Enrollment_Date"].isna()
    ).sum()

    record_result(
        "Required member dates",
        invalid_dates == 0,
        f"Invalid/missing required dates: {invalid_dates:,}."
    )

    dob_after_enrollment = (
        df["Date_of_Birth"]
        > df["Enrollment_Date"]
    ).sum()

    record_result(
        "DOB before enrollment",
        dob_after_enrollment == 0,
        f"DOB after enrollment: {dob_after_enrollment:,}."
    )

    termination_before_enrollment = (
        df["Termination_Date"].notna()
        & (
            df["Termination_Date"]
            < df["Enrollment_Date"]
        )
    ).sum()

    record_result(
        "Termination after enrollment",
        termination_before_enrollment == 0,
        f"Termination before enrollment: {termination_before_enrollment:,}."
    )


# ============================================================
# 6. FACT RECORD COUNT CHECK
# ============================================================

def check_fact_record_counts(
    claims,
    claim_lines,
    payments,
    authorizations
):

    print()
    print("=" * 60)
    print("6. FACT RECORD COUNT CHECK")
    print("=" * 60)

    expected_counts = {
        "Claims": (claims, 101_500),
        "Claim Lines": (claim_lines, 248_547),
        "Payments": (payments, 72_239)
    }

    for name, (
        dataframe,
        expected
    ) in expected_counts.items():

        actual = len(dataframe)

        record_result(
            f"{name} count",
            actual == expected,
            f"Expected {expected:,}; found {actual:,}."
        )

    # Authorization count is intentionally lower
    # because missing-authorization anomalies remove
    # authorization records.

    record_result(
        "Authorization records",
        len(authorizations) > 0,
        f"Authorization records remaining: {len(authorizations):,}."
    )


# ============================================================
# 7. FACT BUSINESS ID CHECK
# ============================================================

def check_fact_ids(
    claims,
    claim_lines,
    payments,
    authorizations
):

    print()
    print("=" * 60)
    print("7. FACT BUSINESS ID CHECK")
    print("=" * 60)

    id_checks = {
        "Claim_ID": claims,
        "Claim_Line_ID": claim_lines,
        "Payment_Reference": payments,
        "Authorization_ID": authorizations
    }

    for column, dataframe in id_checks.items():

        duplicates = (
            dataframe[column]
            .duplicated()
            .sum()
        )

        record_result(
            f"{column} uniqueness",
            duplicates == 0,
            f"Duplicate values: {duplicates:,}."
        )


# ============================================================
# 8. REQUIRED FACT FIELD CHECK
# ============================================================

def check_required_fact_fields(
    claims,
    claim_lines,
    payments,
    authorizations
):

    print()
    print("=" * 60)
    print("8. REQUIRED FACT FIELD CHECK")
    print("=" * 60)

    required_fields = {

        "Claims": (
            claims,
            [
                "Claim_ID",
                "Member_ID",
                "Provider_ID",
                "Plan_ID",
                "Diagnosis_ID",
                "Claim_Date",
                "Claim_Amount"
            ]
        ),

        "Claim Lines": (
            claim_lines,
            [
                "Claim_Line_ID",
                "Claim_ID",
                "Service_ID",
                "Quantity",
                "Unit_Cost",
                "Line_Amount"
            ]
        ),

        "Payments": (
            payments,
            [
                "Payment_Reference",
                "Claim_ID",
                "Payment_Amount"
            ]
        ),

        "Authorizations": (
            authorizations,
            [
                "Authorization_ID",
                "Claim_ID",
                "Member_ID",
                "Provider_ID",
                "Service_ID"
            ]
        )
    }

    for name, (
        dataframe,
        columns
    ) in required_fields.items():

        for column in columns:

            missing = (
                dataframe[column]
                .isna()
                .sum()
            )

            record_result(
                f"{name}.{column}",
                missing == 0,
                f"Missing values: {missing:,}."
            )


# ============================================================
# 9. FACT → DIMENSION REFERENCES
# ============================================================

def check_fact_references(
    claims,
    claim_lines,
    payments,
    authorizations,
    member_df,
    provider_df,
    plan_df,
    diagnosis_df,
    service_df
):

    print()
    print("=" * 60)
    print("9. FACT → DIMENSION REFERENCES")
    print("=" * 60)

    valid_claims = set(
        claims["Claim_ID"]
    )

    valid_members = set(
        member_df["Member_ID"]
    )

    valid_providers = set(
        provider_df["Provider_ID"]
    )

    valid_plans = set(
        plan_df["Plan_ID"]
    )

    valid_diagnoses = set(
        diagnosis_df["Diagnosis_ID"]
    )

    valid_services = set(
        service_df["Service_ID"]
    )

    checks = {

        "Claims → Members":
            (
                ~claims["Member_ID"]
                .isin(valid_members)
            ).sum(),

        "Claims → Providers":
            (
                ~claims["Provider_ID"]
                .isin(valid_providers)
            ).sum(),

        "Claims → Plans":
            (
                ~claims["Plan_ID"]
                .isin(valid_plans)
            ).sum(),

        "Claims → Diagnoses":
            (
                ~claims["Diagnosis_ID"]
                .isin(valid_diagnoses)
            ).sum(),

        "Claim Lines → Claims":
            (
                ~claim_lines["Claim_ID"]
                .isin(valid_claims)
            ).sum(),

        "Claim Lines → Services":
            (
                ~claim_lines["Service_ID"]
                .isin(valid_services)
            ).sum(),

        "Payments → Claims":
            (
                ~payments["Claim_ID"]
                .isin(valid_claims)
            ).sum(),

        "Authorizations → Claims":
            (
                ~authorizations["Claim_ID"]
                .isin(valid_claims)
            ).sum()
    }

    for name, invalid_count in checks.items():

        record_result(
            name,
            invalid_count == 0,
            f"Invalid references: {invalid_count:,}."
        )


# ============================================================
# 10. CLAIM FINANCIAL VALIDATION
# ============================================================

def check_claim_financial_logic(claims):

    print()
    print("=" * 60)
    print("10. CLAIM FINANCIAL VALIDATION")
    print("=" * 60)

    approved_exceeds = (
        claims["Approved_Amount"]
        > claims["Claim_Amount"] + 0.01
    ).sum()

    rejected_exceeds = (
        claims["Rejected_Amount"]
        > claims["Claim_Amount"] + 0.01
    ).sum()

    combined_exceeds = (
        (
            claims["Approved_Amount"]
            + claims["Rejected_Amount"]
        )
        > claims["Claim_Amount"] + 0.01
    ).sum()

    negative_amounts = (
        (
            claims[
                [
                    "Claim_Amount",
                    "Approved_Amount",
                    "Rejected_Amount",
                    "Member_Copay"
                ]
            ]
            < 0
        )
        .any(axis=1)
    ).sum()

    record_result(
        "Approved amount <= claim amount",
        approved_exceeds == 0,
        f"Violations: {approved_exceeds:,}."
    )

    record_result(
        "Rejected amount <= claim amount",
        rejected_exceeds == 0,
        f"Violations: {rejected_exceeds:,}."
    )

    record_result(
        "Approved + Rejected <= claim amount",
        combined_exceeds == 0,
        f"Violations: {combined_exceeds:,}."
    )

    record_result(
        "No negative claim financial values",
        negative_amounts == 0,
        f"Claims with negative financial values: {negative_amounts:,}."
    )


# ============================================================
# 11. CLAIM LINE FINANCIAL VALIDATION
# ============================================================

def check_claim_line_financial_logic(
    claim_lines
):

    print()
    print("=" * 60)
    print("11. CLAIM LINE FINANCIAL VALIDATION")
    print("=" * 60)

    calculated_amount = (
        claim_lines["Quantity"]
        * claim_lines["Unit_Cost"]
    )

    arithmetic_errors = (
        (
            calculated_amount
            - claim_lines["Line_Amount"]
        )
        .abs()
        > 0.01
    ).sum()

    approved_exceeds = (
        claim_lines["Approved_Line_Amount"]
        > claim_lines["Line_Amount"] + 0.01
    ).sum()

    rejected_exceeds = (
        claim_lines["Rejected_Line_Amount"]
        > claim_lines["Line_Amount"] + 0.01
    ).sum()

    invalid_quantity = (
        claim_lines["Quantity"] <= 0
    ).sum()

    negative_values = (
        (
            claim_lines[
                [
                    "Unit_Cost",
                    "Line_Amount",
                    "Approved_Line_Amount",
                    "Rejected_Line_Amount"
                ]
            ]
            < 0
        )
        .any(axis=1)
    ).sum()

    record_result(
        "Line amount arithmetic",
        arithmetic_errors == 0,
        f"Violations: {arithmetic_errors:,}."
    )

    record_result(
        "Approved line amount <= line amount",
        approved_exceeds == 0,
        f"Violations: {approved_exceeds:,}."
    )

    record_result(
        "Rejected line amount <= line amount",
        rejected_exceeds == 0,
        f"Violations: {rejected_exceeds:,}."
    )

    record_result(
        "Positive line quantities",
        invalid_quantity == 0,
        f"Invalid quantities: {invalid_quantity:,}."
    )

    record_result(
        "No negative line financial values",
        negative_values == 0,
        f"Lines with negative financial values: {negative_values:,}."
    )


# ============================================================
# 12. PAYMENT VALIDATION
# ============================================================

def check_payment_logic(
    claims,
    payments
):

    print()
    print("=" * 60)
    print("12. PAYMENT VALIDATION")
    print("=" * 60)

    payment_totals = (
        payments
        .groupby("Claim_ID")["Payment_Amount"]
        .sum()
        .reset_index()
    )

    payment_totals = payment_totals.merge(
        claims[
            [
                "Claim_ID",
                "Approved_Amount"
            ]
        ],
        on="Claim_ID",
        how="left"
    )

    payment_exceeds_approved = (
        payment_totals["Payment_Amount"]
        > payment_totals["Approved_Amount"] + 0.01
    ).sum()

    negative_payments = (
        payments["Payment_Amount"] < 0
    ).sum()

    record_result(
        "Payments <= approved amount",
        payment_exceeds_approved == 0,
        f"Claims where payments exceed approved amount: {payment_exceeds_approved:,}."
    )

    record_result(
        "No negative payments",
        negative_payments == 0,
        f"Negative payment records: {negative_payments:,}."
    )


# ============================================================
# 13. CLAIM DATE VALIDATION
# ============================================================

def check_claim_dates(claims):

    print()
    print("=" * 60)
    print("13. CLAIM DATE VALIDATION")
    print("=" * 60)

    df = claims.copy()

    date_columns = [
        "Claim_Date",
        "Admission_Date",
        "Discharge_Date",
        "Submission_Date",
        "Processing_Date"
    ]

    for column in date_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    invalid_required_dates = (
        df["Claim_Date"].isna()
    ).sum()

    submission_before_claim = (
        df["Submission_Date"]
        < df["Claim_Date"]
    ).sum()

    processed = df[
        df["Processing_Date"].notna()
    ]

    processing_before_submission = (
        processed["Processing_Date"]
        < processed["Submission_Date"]
    ).sum()

    inpatient = df[
        df["Admission_Date"].notna()
        & df["Discharge_Date"].notna()
    ]

    discharge_before_admission = (
        inpatient["Discharge_Date"]
        < inpatient["Admission_Date"]
    ).sum()

    record_result(
        "Valid claim dates",
        invalid_required_dates == 0,
        f"Missing/invalid Claim_Date values: {invalid_required_dates:,}."
    )

    record_result(
        "Submission date >= claim date",
        submission_before_claim == 0,
        f"Violations: {submission_before_claim:,}."
    )

    record_result(
        "Processing date >= submission date",
        processing_before_submission == 0,
        f"Violations: {processing_before_submission:,}."
    )

    record_result(
        "Discharge date >= admission date",
        discharge_before_admission == 0,
        f"Violations: {discharge_before_admission:,}."
    )


# ============================================================
# 14. CLAIM → LINE RECONCILIATION
# ============================================================

def check_claim_line_reconciliation(
    claims,
    claim_lines
):

    print()
    print("=" * 60)
    print("14. CLAIM → LINE RECONCILIATION")
    print("=" * 60)

    line_totals = (
        claim_lines
        .groupby("Claim_ID")["Line_Amount"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "Line_Amount":
                    "Total_Line_Amount"
            }
        )
    )

    reconciliation = claims[
        [
            "Claim_ID",
            "Claim_Amount"
        ]
    ].merge(
        line_totals,
        on="Claim_ID",
        how="left"
    )

    reconciliation[
        "Total_Line_Amount"
    ] = reconciliation[
        "Total_Line_Amount"
    ].fillna(0)

    reconciliation["Difference"] = (
        reconciliation["Claim_Amount"]
        - reconciliation["Total_Line_Amount"]
    )

    mismatches = (
        reconciliation["Difference"]
        .abs()
        > 0.01
    )

    mismatch_count = mismatches.sum()

    total_difference = (
        reconciliation["Difference"]
        .abs()
        .sum()
    )

    record_result(
        "Claim → line reconciliation",
        mismatch_count == 0,
        (
            f"Claims with differences: {mismatch_count:,}; "
            f"total absolute difference: "
            f"₦{total_difference:,.2f}."
        ),
        severity="WARNING"
    )


# ============================================================
# 15. AUTHORIZATION VALIDATION
# ============================================================

def check_authorization_logic(
    claims,
    claim_lines,
    authorizations
):

    print()
    print("=" * 60)
    print("15. AUTHORIZATION VALIDATION")
    print("=" * 60)

    valid_authorizations = set(
        authorizations["Authorization_ID"]
    )

    claim_authorization_ids = (
        claims["Authorization_ID"]
        .dropna()
    )

    invalid_claim_auth_ids = (
        ~claim_authorization_ids
        .isin(valid_authorizations)
    ).sum()

    record_result(
        "Claim Authorization_ID references",
        invalid_claim_auth_ids == 0,
        f"Invalid authorization references: {invalid_claim_auth_ids:,}."
    )

    auth_required = claim_lines[
        claim_lines["Authorization_Required"] == 1
    ]

    missing_required_status = (
        auth_required["Authorization_Status"]
        .isna()
    ).sum()

    record_result(
        "Authorization-required line status",
        missing_required_status == 0,
        f"Missing authorization statuses: {missing_required_status:,}."
    )

    missing_status_count = (
        claim_lines["Authorization_Status"]
        == "Missing"
    ).sum()

    print(
        f"Authorization lines marked Missing: "
        f"{missing_status_count:,}"
    )


# ============================================================
# 16. PLAN COVERAGE VALIDATION
# ============================================================

def check_plan_coverage_logic(
    claims,
    claim_lines,
    member_df,
    plan_df,
    service_df
):

    print()
    print("=" * 60)
    print("16. PLAN COVERAGE VALIDATION")
    print("=" * 60)

    member_plan = member_df[
        [
            "Member_ID",
            "Plan_ID"
        ]
    ].merge(
        plan_df[
            [
                "Plan_ID",
                "Dental_Cover",
                "Optical_Cover",
                "Maternity_Cover"
            ]
        ],
        on="Plan_ID",
        how="left"
    )

    claim_members = claims[
        [
            "Claim_ID",
            "Member_ID"
        ]
    ]

    coverage_df = claim_lines[
        [
            "Claim_ID",
            "Service_ID"
        ]
    ].merge(
        claim_members,
        on="Claim_ID",
        how="left"
    ).merge(
        member_plan,
        on="Member_ID",
        how="left"
    ).merge(
        service_df[
            [
                "Service_ID",
                "Service_Category"
            ]
        ],
        on="Service_ID",
        how="left"
    )

    dental_issues = (
        coverage_df["Service_Category"].eq("Dental")
        & coverage_df["Dental_Cover"].eq(0)
    ).sum()

    optical_issues = (
        coverage_df["Service_Category"].eq("Optical")
        & coverage_df["Optical_Cover"].eq(0)
    ).sum()

    maternity_issues = (
        coverage_df["Service_Category"].eq("Maternity")
        & coverage_df["Maternity_Cover"].eq(0)
    ).sum()

    total_issues = (
        dental_issues
        + optical_issues
        + maternity_issues
    )

    print(
        f"Potential Dental coverage issues: "
        f"{dental_issues:,}"
    )

    print(
        f"Potential Optical coverage issues: "
        f"{optical_issues:,}"
    )

    print(
        f"Potential Maternity coverage issues: "
        f"{maternity_issues:,}"
    )

    print(
        f"Total potential coverage issues: "
        f"{total_issues:,}"
    )

    # These are intentionally injected risk conditions,
    # therefore report them as a warning rather than a failure.

    record_result(
        "Plan coverage consistency",
        total_issues == 0,
        f"Coverage mismatches detected: {total_issues:,}.",
        severity="WARNING"
    )


# ============================================================
# 17. ANOMALY LOG VALIDATION
# ============================================================

def check_anomaly_log():

    print()
    print("=" * 60)
    print("17. ANOMALY LOG VALIDATION")
    print("=" * 60)

    anomaly_log = pd.read_csv(
        VALIDATED_DATA_DIR / "Anomaly_Log.csv"
    )

    duplicate_ids = (
        anomaly_log["Anomaly_ID"]
        .duplicated()
        .sum()
    )

    missing_types = (
        anomaly_log["Anomaly_Type"]
        .isna()
        .sum()
    )

    record_result(
        "Anomaly_ID uniqueness",
        duplicate_ids == 0,
        f"Duplicate anomaly IDs: {duplicate_ids:,}."
    )

    record_result(
        "Anomaly type completeness",
        missing_types == 0,
        f"Missing anomaly types: {missing_types:,}."
    )

    print(
        f"\nTotal anomaly records: "
        f"{len(anomaly_log):,}"
    )

    print("\nAnomalies by type:")

    counts = (
        anomaly_log["Anomaly_Type"]
        .value_counts()
    )

    for anomaly_type, count in counts.items():

        print(
            f"  {anomaly_type}: {count:,}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    global PASS_COUNT
    global WARNING_COUNT
    global FAIL_COUNT

    # Reset counters if main() is called again.
    PASS_COUNT = 0
    WARNING_COUNT = 0
    FAIL_COUNT = 0

    print()
    print("=" * 60)
    print("HMO CLAIMS RISK ANALYTICS")
    print("DATA VALIDATION")
    print("=" * 60)

    print(
        f"Raw dimensions: {RAW_DATA_DIR}"
    )

    print(
        f"Validated facts: {VALIDATED_DATA_DIR}"
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

    (
        hmo_df,
        plan_df,
        member_df,
        provider_df,
        diagnosis_df,
        service_df
    ) = load_dimension_data()

    (
        claims,
        claim_lines,
        payments,
        authorizations,
        anomaly_log
    ) = load_fact_data()

    # ========================================================
    # DIMENSION VALIDATION
    # ========================================================

    check_dimension_record_counts(
        hmo_df,
        plan_df,
        member_df,
        provider_df,
        diagnosis_df,
        service_df
    )

    check_dimension_duplicate_ids(
        hmo_df,
        plan_df,
        member_df,
        provider_df,
        diagnosis_df,
        service_df
    )

    check_hmo_plan_member_relationships(
        hmo_df,
        plan_df,
        member_df
    )

    check_member_quality(
        member_df
    )

    check_member_dates(
        member_df
    )

    # ========================================================
    # FACT VALIDATION
    # ========================================================

    check_fact_record_counts(
        claims,
        claim_lines,
        payments,
        authorizations
    )

    check_fact_ids(
        claims,
        claim_lines,
        payments,
        authorizations
    )

    check_required_fact_fields(
        claims,
        claim_lines,
        payments,
        authorizations
    )

    check_fact_references(
        claims,
        claim_lines,
        payments,
        authorizations,
        member_df,
        provider_df,
        plan_df,
        diagnosis_df,
        service_df
    )

    check_claim_financial_logic(
        claims
    )

    check_claim_line_financial_logic(
        claim_lines
    )

    check_payment_logic(
        claims,
        payments
    )

    check_claim_dates(
        claims
    )

    check_claim_line_reconciliation(
        claims,
        claim_lines
    )

    check_authorization_logic(
        claims,
        claim_lines,
        authorizations
    )

    check_plan_coverage_logic(
        claims,
        claim_lines,
        member_df,
        plan_df,
        service_df
    )

    check_anomaly_log()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 60)

    print(
        f"Passed:   {PASS_COUNT:,}"
    )

    print(
        f"Warnings: {WARNING_COUNT:,}"
    )

    print(
        f"Failed:   {FAIL_COUNT:,}"
    )

    print("=" * 60)

    if FAIL_COUNT == 0:

        print(
            "\nValidation completed with "
            "no critical failures."
        )

    else:

        print(
            "\nValidation completed with "
            f"{FAIL_COUNT:,} critical failure(s)."
        )

    print("=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
