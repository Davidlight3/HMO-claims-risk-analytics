from pathlib import Path
import pandas as pd
import random

from config import (
    PROJECT_ROOT,
    RAW_DATA_DIR,
    VALIDATED_DATA_DIR,
    RANDOM_SEED
)


# ============================================================
# SETUP
# ============================================================

random.seed(RANDOM_SEED)

VALIDATED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    claims = pd.read_csv(
        RAW_DATA_DIR / "Fact_Claims.csv"
    )

    claim_lines = pd.read_csv(
        RAW_DATA_DIR / "Fact_Claim_Lines.csv"
    )

    payments = pd.read_csv(
        RAW_DATA_DIR / "Fact_Payments.csv"
    )

    authorizations = pd.read_csv(
        RAW_DATA_DIR / "Fact_Authorizations.csv"
    )

    members = pd.read_csv(
        RAW_DATA_DIR / "Dim_Member.csv"
    )

    providers = pd.read_csv(
        RAW_DATA_DIR / "Dim_Provider.csv"
    )

    plans = pd.read_csv(
        RAW_DATA_DIR / "Dim_Plan.csv"
    )

    services = pd.read_csv(
        RAW_DATA_DIR / "Dim_Service.csv"
    )

    return (
        claims,
        claim_lines,
        payments,
        authorizations,
        members,
        providers,
        plans,
        services
    )


# ============================================================
# ANOMALY LOG
# ============================================================

def create_anomaly_log():

    return pd.DataFrame(
        columns=[
            "Anomaly_ID",
            "Anomaly_Type",
            "Claim_ID",
            "Claim_Line_ID",
            "Member_ID",
            "Provider_ID",
            "Description"
        ]
    )

# ============================================================
# HIGH-VALUE CLAIM ANOMALIES
# ============================================================

def inject_high_value_claims(
    claims,
    anomaly_log,
    percentage=0.02
):

    print("\nInjecting high-value claim anomalies...")

    number_to_inject = int(
        len(claims) * percentage
    )

    selected_indices = random.sample(
        list(claims.index),
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    for index in selected_indices:

        old_amount = float(
            claims.at[index, "Claim_Amount"]
        )

        # Generate an unusually high claim amount
        new_amount = round(
            random.uniform(600000, 1500000),
            2
        )

        claims.at[index, "Claim_Amount"] = new_amount

        # Keep approved/rejected amounts logically consistent
        status = claims.at[index, "Claim_Status"]

        if status == "Approved":

            claims.at[index, "Approved_Amount"] = new_amount
            claims.at[index, "Rejected_Amount"] = 0

        elif status == "Partially Approved":

            approval_ratio = random.uniform(
                0.40,
                0.80
            )

            approved_amount = round(
                new_amount * approval_ratio,
                2
            )

            rejected_amount = round(
                new_amount - approved_amount,
                2
            )

            claims.at[index, "Approved_Amount"] = (
                approved_amount
            )

            claims.at[index, "Rejected_Amount"] = (
                rejected_amount
            )

        elif status == "Rejected":

            claims.at[index, "Approved_Amount"] = 0
            claims.at[index, "Rejected_Amount"] = new_amount

        else:
            # Pending claim
            claims.at[index, "Approved_Amount"] = 0
            claims.at[index, "Rejected_Amount"] = 0

        claim_id = claims.at[
            index,
            "Claim_ID"
        ]

        member_id = claims.at[
            index,
            "Member_ID"
        ]

        provider_id = claims.at[
            index,
            "Provider_ID"
        ]

        anomaly_log.loc[len(anomaly_log)] = {
            "Anomaly_ID": f"ANM{anomaly_counter:06d}",
            "Anomaly_Type": "High-Value Claim",
            "Claim_ID": claim_id,
            "Claim_Line_ID": None,
            "Member_ID": member_id,
            "Provider_ID": provider_id,
            "Description": (
                f"Claim amount increased from "
                f"{old_amount:,.2f} to "
                f"{new_amount:,.2f}"
            )
        }

        anomaly_counter += 1

    print(
        f"High-value claims injected: "
        f"{number_to_inject:,}"
    )

    return claims, anomaly_log
# ============================================================
# DUPLICATE CLAIM ANOMALIES
# ============================================================

def inject_duplicate_claims(
    claims,
    claim_lines,
    anomaly_log,
    percentage=0.015
):

    print("\nInjecting duplicate claim anomalies...")

    number_to_inject = int(
        len(claims) * percentage
    )

    # Select original claims to duplicate
    selected_indices = random.sample(
        list(claims.index),
        number_to_inject
    )

    duplicate_claims = []
    duplicate_lines = []

    anomaly_counter = len(anomaly_log) + 1

    next_claim_number = len(claims) + 1
    next_line_number = len(claim_lines) + 1

    for index in selected_indices:

        original_claim = claims.loc[index].copy()

        original_claim_id = original_claim["Claim_ID"]

        # ----------------------------------------------------
        # Create a new Claim ID
        # ----------------------------------------------------

        new_claim_id = (
            f"CLM{next_claim_number:07d}"
        )

        duplicate_claim = original_claim.copy()

        duplicate_claim["Claim_ID"] = new_claim_id

        duplicate_claims.append(
            duplicate_claim
        )

        # ----------------------------------------------------
        # Duplicate claim lines
        # ----------------------------------------------------

        original_lines = claim_lines[
            claim_lines["Claim_ID"] == original_claim_id
        ]

        for _, line in original_lines.iterrows():

            duplicate_line = line.copy()

            new_line_id = (
                f"CL{next_line_number:08d}"
            )

            duplicate_line[
                "Claim_Line_ID"
            ] = new_line_id

            duplicate_line[
                "Claim_ID"
            ] = new_claim_id

            duplicate_lines.append(
                duplicate_line
            )

            next_line_number += 1

        # ----------------------------------------------------
        # Record anomaly
        # ----------------------------------------------------

        anomaly_log.loc[len(anomaly_log)] = {
            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Potential Duplicate Claim",

            "Claim_ID":
                new_claim_id,

            "Claim_Line_ID":
                None,

            "Member_ID":
                duplicate_claim["Member_ID"],

            "Provider_ID":
                duplicate_claim["Provider_ID"],

            "Description":
                (
                    f"Potential duplicate of "
                    f"{original_claim_id}"
                )
        }

        anomaly_counter += 1
        next_claim_number += 1

    # --------------------------------------------------------
    # Append duplicated claims
    # --------------------------------------------------------

    duplicate_claims_df = pd.DataFrame(
        duplicate_claims
    )

    claims = pd.concat(
        [
            claims,
            duplicate_claims_df
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Append duplicated claim lines
    # --------------------------------------------------------

    if duplicate_lines:

        duplicate_lines_df = pd.DataFrame(
            duplicate_lines
        )

        claim_lines = pd.concat(
            [
                claim_lines,
                duplicate_lines_df
            ],
            ignore_index=True
        )

    print(
        f"Duplicate claims injected: "
        f"{number_to_inject:,}"
    )

    print(
        f"New claim count: "
        f"{len(claims):,}"
    )

    print(
        f"New claim-line count: "
        f"{len(claim_lines):,}"
    )

    return (
        claims,
        claim_lines,
        anomaly_log
    )
# ============================================================
# EXCESSIVE MEMBER FREQUENCY ANOMALIES
# ============================================================

def inject_excessive_member_frequency(
    claims,
    anomaly_log,
    percentage=0.015
):

    print("\nInjecting excessive member frequency anomalies...")

    # Number of members to affect
    number_of_members = int(
        claims["Member_ID"].nunique() * percentage
    )

    # Select members
    member_ids = random.sample(
        list(claims["Member_ID"].unique()),
        number_of_members
    )

    anomaly_counter = len(anomaly_log) + 1

    total_claims_affected = 0

    for member_id in member_ids:

        # Get this member's claims
        member_claim_indices = list(
            claims[
                claims["Member_ID"] == member_id
            ].index
        )

        # Need enough claims to create a meaningful pattern
        if len(member_claim_indices) < 6:
            continue

        # Select 6–12 claims
        number_of_claims = min(
            random.randint(6, 12),
            len(member_claim_indices)
        )

        selected_indices = random.sample(
            member_claim_indices,
            number_of_claims
        )

        # Choose a starting date from one of the selected claims
        base_index = selected_indices[0]

        base_date = pd.to_datetime(
            claims.at[
                base_index,
                "Claim_Date"
            ]
        )

        # Concentrate claims within 30 days
        for index in selected_indices:

            new_date = (
                base_date
                + pd.Timedelta(
                    days=random.randint(0, 30)
                )
            )

            claims.at[
                index,
                "Claim_Date"
            ] = new_date.strftime(
                "%Y-%m-%d"
            )

            # Keep submission date logically after claim date
            submission_date = (
                new_date
                + pd.Timedelta(
                    days=random.randint(0, 3)
                )
            )

            claims.at[
                index,
                "Submission_Date"
            ] = submission_date.strftime(
                "%Y-%m-%d"
            )

            # Processing date must be after submission
            if claims.at[
                index,
                "Claim_Status"
            ] == "Pending":

                claims.at[
                    index,
                    "Processing_Date"
                ] = None

            else:

                processing_date = (
                    submission_date
                    + pd.Timedelta(
                        days=random.randint(1, 7)
                    )
                )

                claims.at[
                    index,
                    "Processing_Date"
                ] = processing_date.strftime(
                    "%Y-%m-%d"
                )

            claim_id = claims.at[
                index,
                "Claim_ID"
            ]

            provider_id = claims.at[
                index,
                "Provider_ID"
            ]

            anomaly_log.loc[
                len(anomaly_log)
            ] = {

                "Anomaly_ID":
                    f"ANM{anomaly_counter:06d}",

                "Anomaly_Type":
                    "Excessive Member Frequency",

                "Claim_ID":
                    claim_id,

                "Claim_Line_ID":
                    None,

                "Member_ID":
                    member_id,

                "Provider_ID":
                    provider_id,

                "Description":
                    (
                        f"Member {member_id} has "
                        f"{number_of_claims} claims "
                        f"concentrated within "
                        f"a 30-day period."
                    )
            }

            anomaly_counter += 1
            total_claims_affected += 1

    print(
        f"Members targeted: "
        f"{number_of_members:,}"
    )

    print(
        f"Claims affected by frequency anomaly: "
        f"{total_claims_affected:,}"
    )

    return claims, anomaly_log
# ============================================================
# PROVIDER RISK ANOMALIES
# ============================================================

def inject_provider_risk(
    claims,
    providers,
    anomaly_log,
    number_of_providers=12
):

    print("\nInjecting provider risk anomalies...")

    provider_ids = list(
        providers["Provider_ID"].unique()
    )

    selected_providers = random.sample(
        provider_ids,
        number_of_providers
    )

    anomaly_counter = len(anomaly_log) + 1
    total_claims_affected = 0

    # --------------------------------------------------------
    # Calculate how many claims to assign to each provider
    # --------------------------------------------------------

    for provider_id in selected_providers:

        # Select approximately 0.15%–0.30% of all claims
        number_of_claims = random.randint(
            150,
            300
        )

        available_indices = list(
            claims.index
        )

        selected_indices = random.sample(
            available_indices,
            number_of_claims
        )

        for index in selected_indices:

            # ------------------------------------------------
            # Assign claim to high-risk provider
            # ------------------------------------------------

            claims.at[
                index,
                "Provider_ID"
            ] = provider_id

            # ------------------------------------------------
            # Increase claim value
            # ------------------------------------------------

            old_amount = float(
                claims.at[
                    index,
                    "Claim_Amount"
                ]
            )

            multiplier = random.uniform(
                1.5,
                3.0
            )

            new_amount = round(
                old_amount * multiplier,
                2
            )

            claims.at[
                index,
                "Claim_Amount"
            ] = new_amount

            # ------------------------------------------------
            # Maintain financial consistency
            # ------------------------------------------------

            status = claims.at[
                index,
                "Claim_Status"
            ]

            if status == "Approved":

                claims.at[
                    index,
                    "Approved_Amount"
                ] = new_amount

                claims.at[
                    index,
                    "Rejected_Amount"
                ] = 0

            elif status == "Partially Approved":

                approval_ratio = random.uniform(
                    0.40,
                    0.80
                )

                approved_amount = round(
                    new_amount * approval_ratio,
                    2
                )

                rejected_amount = round(
                    new_amount - approved_amount,
                    2
                )

                claims.at[
                    index,
                    "Approved_Amount"
                ] = approved_amount

                claims.at[
                    index,
                    "Rejected_Amount"
                ] = rejected_amount

            elif status == "Rejected":

                claims.at[
                    index,
                    "Approved_Amount"
                ] = 0

                claims.at[
                    index,
                    "Rejected_Amount"
                ] = new_amount

            else:

                claims.at[
                    index,
                    "Approved_Amount"
                ] = 0

                claims.at[
                    index,
                    "Rejected_Amount"
                ] = 0

            # ------------------------------------------------
            # Record anomaly
            # ------------------------------------------------

            claim_id = claims.at[
                index,
                "Claim_ID"
            ]

            member_id = claims.at[
                index,
                "Member_ID"
            ]

            anomaly_log.loc[
                len(anomaly_log)
            ] = {

                "Anomaly_ID":
                    f"ANM{anomaly_counter:06d}",

                "Anomaly_Type":
                    "Provider Risk",

                "Claim_ID":
                    claim_id,

                "Claim_Line_ID":
                    None,

                "Member_ID":
                    member_id,

                "Provider_ID":
                    provider_id,

                "Description":
                    (
                        "Claim assigned to selected "
                        "high-risk provider and claim "
                        "value increased."
                    )
            }

            anomaly_counter += 1
            total_claims_affected += 1

    print(
        f"High-risk providers targeted: "
        f"{number_of_providers}"
    )

    print(
        f"Claims affected by provider anomalies: "
        f"{total_claims_affected:,}"
    )

    return claims, anomaly_log
# ============================================================
# SERVICE COST ANOMALIES
# ============================================================

def inject_service_cost_anomalies(
    claim_lines,
    services,
    anomaly_log,
    percentage=0.015
):

    print("\nInjecting service cost anomalies...")

    number_to_inject = int(
        len(claim_lines) * percentage
    )

    selected_indices = random.sample(
        list(claim_lines.index),
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    for index in selected_indices:

        service_id = claim_lines.at[
            index,
            "Service_ID"
        ]

        service_match = services[
            services["Service_ID"] == service_id
        ]

        if service_match.empty:
            continue

        standard_cost = float(
            service_match.iloc[0][
                "Standard_Unit_Cost"
            ]
        )

        old_line_amount = float(
            claim_lines.at[
                index,
                "Line_Amount"
            ]
        )

        old_approved = float(
            claim_lines.at[
                index,
                "Approved_Line_Amount"
            ]
        )

        old_rejected = float(
            claim_lines.at[
                index,
                "Rejected_Line_Amount"
            ]
        )

        quantity = int(
            claim_lines.at[
                index,
                "Quantity"
            ]
        )

        # Create abnormal unit cost
        multiplier = random.uniform(
            2.0,
            5.0
        )

        new_unit_cost = round(
            standard_cost * multiplier,
            2
        )

        new_line_amount = round(
            new_unit_cost * quantity,
            2
        )

        # Preserve approval/rejection proportions
        if old_line_amount > 0:

            approval_ratio = (
                old_approved /
                old_line_amount
            )

            rejection_ratio = (
                old_rejected /
                old_line_amount
            )

        else:

            approval_ratio = 0
            rejection_ratio = 0

        new_approved = round(
            new_line_amount * approval_ratio,
            2
        )

        new_rejected = round(
            new_line_amount * rejection_ratio,
            2
        )

        if new_approved + new_rejected > new_line_amount:
            new_rejected = round(
                max(
                    0,
                    new_line_amount - new_approved
                ),
                2
            )

        # Update values
        claim_lines.at[
            index,
            "Unit_Cost"
        ] = new_unit_cost

        claim_lines.at[
            index,
            "Line_Amount"
        ] = new_line_amount

        claim_lines.at[
            index,
            "Approved_Line_Amount"
        ] = new_approved

        claim_lines.at[
            index,
            "Rejected_Line_Amount"
        ] = new_rejected

        # Record anomaly
        claim_id = claim_lines.at[
            index,
            "Claim_ID"
        ]

        claim_line_id = claim_lines.at[
            index,
            "Claim_Line_ID"
        ]

        anomaly_log.loc[
            len(anomaly_log)
        ] = {

            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Service Cost Anomaly",

            "Claim_ID":
                claim_id,

            "Claim_Line_ID":
                claim_line_id,

            "Member_ID":
                None,

            "Provider_ID":
                None,

            "Description":
                (
                    f"Service {service_id} unit cost "
                    f"increased from standard cost "
                    f"₦{standard_cost:,.2f} to "
                    f"₦{new_unit_cost:,.2f}."
                )
        }

        anomaly_counter += 1

    print(
        f"Service cost anomalies injected: "
        f"{number_to_inject:,}"
    )

    return claim_lines, anomaly_log
# ============================================================
# EXCESSIVE QUANTITY ANOMALIES
# ============================================================

def inject_excessive_quantity(
    claim_lines,
    anomaly_log,
    percentage=0.01
):

    print("\nInjecting excessive quantity anomalies...")

    number_to_inject = int(
        len(claim_lines) * percentage
    )

    selected_indices = random.sample(
        list(claim_lines.index),
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    for index in selected_indices:

        # ----------------------------------------------------
        # Capture original values
        # ----------------------------------------------------

        old_quantity = int(
            claim_lines.at[
                index,
                "Quantity"
            ]
        )

        old_line_amount = float(
            claim_lines.at[
                index,
                "Line_Amount"
            ]
        )

        old_approved = float(
            claim_lines.at[
                index,
                "Approved_Line_Amount"
            ]
        )

        old_rejected = float(
            claim_lines.at[
                index,
                "Rejected_Line_Amount"
            ]
        )

        # ----------------------------------------------------
        # Create unusually high quantity
        # ----------------------------------------------------

        new_quantity = random.randint(
            6,
            15
        )

        # ----------------------------------------------------
        # Calculate new unit cost
        #
        # Keep the original line amount conceptually unchanged,
        # but derive a new unit cost from the excessive quantity.
        # ----------------------------------------------------

        if new_quantity > 0:

            new_unit_cost = round(
                old_line_amount / new_quantity,
                2
            )

        else:

            new_unit_cost = 0.00

        # ----------------------------------------------------
        # Recalculate line amount using the final rounded
        # unit cost so:
        #
        # Quantity × Unit_Cost = Line_Amount
        # ----------------------------------------------------

        new_line_amount = round(
            new_unit_cost * new_quantity,
            2
        )

        # ----------------------------------------------------
        # Preserve the original approval/rejection proportions
        # ----------------------------------------------------

        if old_line_amount > 0:

            approval_ratio = (
                old_approved /
                old_line_amount
            )

            rejection_ratio = (
                old_rejected /
                old_line_amount
            )

        else:

            approval_ratio = 0.0
            rejection_ratio = 0.0

        # ----------------------------------------------------
        # Calculate proportional approved amount
        # ----------------------------------------------------

        new_approved = round(
            new_line_amount * approval_ratio,
            2
        )

        # ----------------------------------------------------
        # Never allow approved amount to exceed line amount
        # ----------------------------------------------------

        new_approved = min(
            max(
                new_approved,
                0.00
            ),
            new_line_amount
        )

        # ----------------------------------------------------
        # Calculate remaining amount available for rejection
        # ----------------------------------------------------

        remaining_amount = round(
            max(
                0.00,
                new_line_amount - new_approved
            ),
            2
        )

        # ----------------------------------------------------
        # Calculate proportional rejected amount
        # ----------------------------------------------------

        new_rejected = round(
            new_line_amount * rejection_ratio,
            2
        )

        # ----------------------------------------------------
        # Never allow rejected amount to exceed either:
        #
        # 1. Line amount
        # 2. Remaining amount after approval
        # ----------------------------------------------------

        new_rejected = min(
            max(
                new_rejected,
                0.00
            ),
            remaining_amount
        )

        # ----------------------------------------------------
        # Final rounding
        # ----------------------------------------------------

        new_approved = round(
            new_approved,
            2
        )

        new_rejected = round(
            new_rejected,
            2
        )

        # ----------------------------------------------------
        # Final defensive integrity check
        # ----------------------------------------------------

        if (
            new_approved +
            new_rejected
        ) > new_line_amount:

            new_rejected = round(
                max(
                    0.00,
                    new_line_amount - new_approved
                ),
                2
            )

        # ----------------------------------------------------
        # Update claim line
        # ----------------------------------------------------

        claim_lines.at[
            index,
            "Quantity"
        ] = new_quantity

        claim_lines.at[
            index,
            "Unit_Cost"
        ] = new_unit_cost

        claim_lines.at[
            index,
            "Line_Amount"
        ] = new_line_amount

        claim_lines.at[
            index,
            "Approved_Line_Amount"
        ] = new_approved

        claim_lines.at[
            index,
            "Rejected_Line_Amount"
        ] = new_rejected

        # ----------------------------------------------------
        # Record anomaly
        # ----------------------------------------------------

        claim_id = claim_lines.at[
            index,
            "Claim_ID"
        ]

        claim_line_id = claim_lines.at[
            index,
            "Claim_Line_ID"
        ]

        anomaly_log.loc[
            len(anomaly_log)
        ] = {

            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Excessive Quantity",

            "Claim_ID":
                claim_id,

            "Claim_Line_ID":
                claim_line_id,

            "Member_ID":
                None,

            "Provider_ID":
                None,

            "Description":
                (
                    f"Service quantity increased "
                    f"from {old_quantity} "
                    f"to {new_quantity}."
                )
        }

        anomaly_counter += 1

    print(
        f"Excessive quantity anomalies injected: "
        f"{number_to_inject:,}"
    )

    return claim_lines, anomaly_log
# ============================================================
# SUSPICIOUS TIMING ANOMALIES
# ============================================================

def inject_suspicious_timing(
    claims,
    anomaly_log,
    percentage=0.01
):

    print("\nInjecting suspicious timing anomalies...")

    number_to_inject = int(
        len(claims) * percentage
    )

    selected_indices = random.sample(
        list(claims.index),
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    for index in selected_indices:

        claim_date = pd.to_datetime(
            claims.at[
                index,
                "Claim_Date"
            ]
        )

        # ----------------------------------------------------
        # Create unusually long submission delay
        # ----------------------------------------------------

        submission_delay = random.randint(
            30,
            90
        )

        submission_date = (
            claim_date
            + pd.Timedelta(
                days=submission_delay
            )
        )

        claims.at[
            index,
            "Submission_Date"
        ] = submission_date.strftime(
            "%Y-%m-%d"
        )

        # ----------------------------------------------------
        # Processing date
        # ----------------------------------------------------

        if claims.at[
            index,
            "Claim_Status"
        ] == "Pending":

            claims.at[
                index,
                "Processing_Date"
            ] = None

        else:

            processing_date = (
                submission_date
                + pd.Timedelta(
                    days=random.randint(1, 14)
                )
            )

            claims.at[
                index,
                "Processing_Date"
            ] = processing_date.strftime(
                "%Y-%m-%d"
            )

        # ----------------------------------------------------
        # Record anomaly
        # ----------------------------------------------------

        claim_id = claims.at[
            index,
            "Claim_ID"
        ]

        member_id = claims.at[
            index,
            "Member_ID"
        ]

        provider_id = claims.at[
            index,
            "Provider_ID"
        ]

        anomaly_log.loc[
            len(anomaly_log)
        ] = {

            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Suspicious Timing",

            "Claim_ID":
                claim_id,

            "Claim_Line_ID":
                None,

            "Member_ID":
                member_id,

            "Provider_ID":
                provider_id,

            "Description":
                (
                    f"Claim submitted "
                    f"{submission_delay} days "
                    f"after claim date."
                )
        }

        anomaly_counter += 1

    print(
        f"Suspicious timing anomalies injected: "
        f"{number_to_inject:,}"
    )

    return claims, anomaly_log
# ============================================================
# MISSING AUTHORIZATION ANOMALIES
# ============================================================

def inject_missing_authorization(
    claims,
    claim_lines,
    authorizations,
    anomaly_log,
    percentage=0.02
):

    print("\nInjecting missing authorization anomalies...")

    # --------------------------------------------------------
    # Identify claim lines that require authorization
    # --------------------------------------------------------

    eligible_lines = claim_lines[
        claim_lines["Authorization_Required"] == 1
    ]

    if eligible_lines.empty:

        print(
            "No authorization-required claim lines found."
        )

        return (
            claims,
            claim_lines,
            authorizations,
            anomaly_log
        )

    number_to_inject = int(
        len(eligible_lines) * percentage
    )

    selected_indices = random.sample(
        list(eligible_lines.index),
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    affected_claim_ids = set()

    for index in selected_indices:

        claim_id = claim_lines.at[
            index,
            "Claim_ID"
        ]

        claim_line_id = claim_lines.at[
            index,
            "Claim_Line_ID"
        ]

        # ----------------------------------------------------
        # Remove authorization from claim line
        # ----------------------------------------------------

        claim_lines.at[
            index,
            "Authorization_Status"
        ] = "Missing"

        # ----------------------------------------------------
        # Remove authorization reference from claim(s)
        # ----------------------------------------------------

        claim_mask = (
            claims["Claim_ID"] == claim_id
        )

        # Duplicate claims can inherit the same Authorization_ID.
        # Capture the ID first, then clear every claim that points to
        # that authorization so no orphan Authorization_ID remains.
        authorization_id = None
        if claim_mask.any():
            authorization_id = claims.loc[
                claim_mask,
                "Authorization_ID"
            ].iloc[0]

        if pd.notna(authorization_id):
            shared_auth_mask = (
                claims["Authorization_ID"] == authorization_id
            )
            shared_claim_ids = claims.loc[
                shared_auth_mask,
                "Claim_ID"
            ].tolist()
            claims.loc[
                shared_auth_mask,
                "Authorization_ID"
            ] = None
            affected_claim_ids.update(shared_claim_ids)
        else:
            claims.loc[
                claim_mask,
                "Authorization_ID"
            ] = None
            affected_claim_ids.add(claim_id)

        # ----------------------------------------------------
        # Remove matching authorization record(s)
        # ----------------------------------------------------

        if pd.notna(authorization_id):
            authorization_mask = (
                authorizations["Authorization_ID"]
                == authorization_id
            )
        else:
            authorization_mask = (
                authorizations["Claim_ID"] == claim_id
            )

        authorizations = authorizations[
            ~authorization_mask
        ].copy()

        # ----------------------------------------------------
        # Record anomaly
        # ----------------------------------------------------

        member_id = claims.loc[
            claim_mask,
            "Member_ID"
        ].iloc[0]

        provider_id = claims.loc[
            claim_mask,
            "Provider_ID"
        ].iloc[0]

        service_id = claim_lines.at[
            index,
            "Service_ID"
        ]

        anomaly_log.loc[
            len(anomaly_log)
        ] = {

            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Missing Authorization",

            "Claim_ID":
                claim_id,

            "Claim_Line_ID":
                claim_line_id,

            "Member_ID":
                member_id,

            "Provider_ID":
                provider_id,

            "Description":
                (
                    f"Service {service_id} requires "
                    f"authorization but no valid "
                    f"authorization record exists."
                )
        }

        anomaly_counter += 1

    print(
        f"Authorization-required lines available: "
        f"{len(eligible_lines):,}"
    )

    print(
        f"Missing authorization anomalies injected: "
        f"{number_to_inject:,}"
    )

    print(
        f"Claims affected: "
        f"{len(affected_claim_ids):,}"
    )

    return (
        claims,
        claim_lines,
        authorizations,
        anomaly_log
    )
# ============================================================
# PLAN COVERAGE ANOMALIES
# ============================================================

def inject_plan_coverage_issues(
    claims,
    claim_lines,
    members,
    plans,
    services,
    anomaly_log,
    percentage=0.01
):

    print("\nInjecting plan coverage anomalies...")

    # ========================================================
    # PREPARE MEMBER → PLAN MAPPING
    # ========================================================

    member_plan = members[
        [
            "Member_ID",
            "Plan_ID"
        ]
    ].merge(
        plans[
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

    # ========================================================
    # PREPARE SERVICE CATEGORIES
    # ========================================================

    dental_services = services[
        services["Service_ID"].isin(
            ["S026", "S027"]
        )
    ]

    optical_services = services[
        services["Service_ID"].isin(
            ["S028", "S029"]
        )
    ]

    maternity_services = services[
        services["Service_ID"].isin(
            ["S022"]
        )
    ]

    # ========================================================
    # BUILD ELIGIBLE CLAIM LINES
    # ========================================================

    claim_member_map = claims[
        [
            "Claim_ID",
            "Member_ID",
            "Provider_ID"
        ]
    ]

    eligible_lines = claim_lines.merge(
        claim_member_map,
        on="Claim_ID",
        how="left"
    ).merge(
        member_plan,
        on="Member_ID",
        how="left"
    )

    # ========================================================
    # IDENTIFY COVERAGE-ISSUE CANDIDATES
    # ========================================================

    candidates = []

    for index, row in eligible_lines.iterrows():

        dental_not_covered = (
            row["Dental_Cover"] == 0
            and not dental_services.empty
        )

        optical_not_covered = (
            row["Optical_Cover"] == 0
            and not optical_services.empty
        )

        maternity_not_covered = (
            row["Maternity_Cover"] == 0
            and not maternity_services.empty
        )

        if dental_not_covered:
            candidates.append(
                (
                    index,
                    "Dental",
                    dental_services
                )
            )

        elif optical_not_covered:
            candidates.append(
                (
                    index,
                    "Optical",
                    optical_services
                )

            )

        elif maternity_not_covered:
            candidates.append(
                (
                    index,
                    "Maternity",
                    maternity_services
                )
            )

    # ========================================================
    # CHECK AVAILABLE CANDIDATES
    # ========================================================

    if not candidates:

        print(
            "No eligible plan coverage candidates found."
        )

        return (
            claims,
            claim_lines,
            anomaly_log
        )

    # ========================================================
    # DETERMINE NUMBER OF ANOMALIES
    # ========================================================

    number_to_inject = int(
        len(claim_lines) * percentage
    )

    number_to_inject = min(
        number_to_inject,
        len(candidates)
    )

    selected_candidates = random.sample(
        candidates,
        number_to_inject
    )

    anomaly_counter = len(anomaly_log) + 1

    # ========================================================
    # INJECT PLAN COVERAGE ISSUES
    # ========================================================

    for (
        eligible_index,
        coverage_type,
        service_pool
    ) in selected_candidates:

        # ----------------------------------------------------
        # Locate original claim line
        # ----------------------------------------------------

        claim_id = eligible_lines.loc[
            eligible_index,
            "Claim_ID"
        ]

        claim_line_id = eligible_lines.loc[
            eligible_index,
            "Claim_Line_ID"
        ]

        member_id = eligible_lines.loc[
            eligible_index,
            "Member_ID"
        ]

        provider_id = eligible_lines.loc[
            eligible_index,
            "Provider_ID"
        ]

        # ----------------------------------------------------
        # Find actual claim-line index
        # ----------------------------------------------------

        line_mask = (
            claim_lines["Claim_Line_ID"]
            == claim_line_id
        )

        if not line_mask.any():
            continue

        line_index = claim_lines.index[
            line_mask
        ][0]

        # ----------------------------------------------------
        # Select an uncovered service
        # ----------------------------------------------------

        selected_service = service_pool.sample(
            n=1,
            random_state=random.randint(
                1,
                1_000_000
            )
        ).iloc[0]

        old_service_id = claim_lines.at[
            line_index,
            "Service_ID"
        ]

        new_service_id = selected_service[
            "Service_ID"
        ]

        # ----------------------------------------------------
        # Avoid changing a line to the same service
        # ----------------------------------------------------

        if old_service_id == new_service_id:
            continue

        # ----------------------------------------------------
        # Preserve financial values
        # ----------------------------------------------------

        # Coverage anomalies are business-rule anomalies. We intentionally
        # keep the existing financial values unchanged so the anomaly does
        # not create unrelated payment or claim-financial failures.

        # ----------------------------------------------------
        # Update claim line service only
        # ----------------------------------------------------

        claim_lines.at[
            line_index,
            "Service_ID"
        ] = new_service_id

        # ----------------------------------------------------
        # Update authorization requirement
        # ----------------------------------------------------

        authorization_required = int(
            selected_service[
                "Requires_Authorization"
            ]
        )

        claim_lines.at[
            line_index,
            "Authorization_Required"
        ] = authorization_required

        if authorization_required == 1:

            claim_lines.at[
                line_index,
                "Authorization_Status"
            ] = "Required"

        else:

            claim_lines.at[
                line_index,
                "Authorization_Status"
            ] = "Not Required"

        # ----------------------------------------------------
        # Claim-level financial values remain unchanged
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Record anomaly
        # ----------------------------------------------------

        anomaly_log.loc[
            len(anomaly_log)
        ] = {

            "Anomaly_ID":
                f"ANM{anomaly_counter:06d}",

            "Anomaly_Type":
                "Plan Coverage Issue",

            "Claim_ID":
                claim_id,

            "Claim_Line_ID":
                claim_line_id,

            "Member_ID":
                member_id,

            "Provider_ID":
                provider_id,

            "Description":
                (
                    f"Service changed from "
                    f"{old_service_id} to "
                    f"{new_service_id} "
                    f"({coverage_type}) because "
                    f"the member's plan does not "
                    f"include this coverage."
                )
        }

        anomaly_counter += 1

    

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        f"Plan coverage anomalies injected: "
        f"{number_to_inject:,}"
    )

    print(
        f"Eligible coverage candidates: "
        f"{len(candidates):,}"
    )

    return (
        claims,
        claim_lines,
        anomaly_log
    )
    
# ============================================================
# FINAL CLAIM-LINE FINANCIAL RECONCILIATION
# ============================================================

def reconcile_claim_lines(claim_lines):
    """Final reconciliation of claim-line approval/rejection amounts."""
    if claim_lines.empty:
        return claim_lines

    claim_lines = claim_lines.copy()

    for column in ["Line_Amount", "Approved_Line_Amount", "Rejected_Line_Amount"]:
        claim_lines[column] = (
            pd.to_numeric(claim_lines[column], errors="coerce")
            .fillna(0)
            .clip(lower=0)
            .round(2)
        )

    claim_lines["Approved_Line_Amount"] = (
        claim_lines[["Approved_Line_Amount", "Line_Amount"]]
        .min(axis=1)
        .round(2)
    )

    remaining = (
        claim_lines["Line_Amount"]
        - claim_lines["Approved_Line_Amount"]
    ).clip(lower=0).round(2)

    claim_lines["Rejected_Line_Amount"] = (
        claim_lines[["Rejected_Line_Amount"]]
        .assign(_remaining=remaining)[["Rejected_Line_Amount", "_remaining"]]
        .min(axis=1)
        .round(2)
    )

    return claim_lines


# ============================================================
# FINAL PAYMENT INTEGRITY RECONCILIATION
# ============================================================

def reconcile_payments_to_claims(claims, payments):
    """Ensure cumulative payments per claim do not exceed final approval."""
    if payments.empty:
        return payments

    payments = payments.copy()
    approved_map = claims.set_index("Claim_ID")["Approved_Amount"]
    payments["Final_Approved_Amount"] = (
        payments["Claim_ID"].map(approved_map).fillna(0).clip(lower=0).round(2)
    )

    sort_columns = ["Claim_ID"]
    if "Payment_Date" in payments.columns:
        sort_columns.append("Payment_Date")
    if "Payment_Reference" in payments.columns:
        sort_columns.append("Payment_Reference")
    payments = payments.sort_values(sort_columns).copy()

    payments["Payment_Amount"] = (
        pd.to_numeric(payments["Payment_Amount"], errors="coerce")
        .fillna(0).clip(lower=0).round(2)
    )
    payments["Previous_Payment_Total"] = (
        payments.groupby("Claim_ID")["Payment_Amount"].cumsum()
        - payments["Payment_Amount"]
    )
    payments["Remaining_Approved"] = (
        payments["Final_Approved_Amount"] - payments["Previous_Payment_Total"]
    ).clip(lower=0).round(2)
    payments["Payment_Amount"] = (
        payments[["Payment_Amount", "Remaining_Approved"]]
        .min(axis=1).clip(lower=0).round(2)
    )
    payments.drop(columns=["Final_Approved_Amount", "Previous_Payment_Total", "Remaining_Approved"], inplace=True)
    return payments


# ============================================================
# SAVE DATA
# ============================================================

def save_data(
    claims,
    claim_lines,
    payments,
    authorizations,
    anomaly_log
):

    claims.to_csv(
        VALIDATED_DATA_DIR / "Fact_Claims.csv",
        index=False
    )

    claim_lines.to_csv(
        VALIDATED_DATA_DIR / "Fact_Claim_Lines.csv",
        index=False
    )

    payments.to_csv(
        VALIDATED_DATA_DIR / "Fact_Payments.csv",
        index=False
    )

    authorizations.to_csv(
        VALIDATED_DATA_DIR / "Fact_Authorizations.csv",
        index=False
    )

    anomaly_log.to_csv(
        VALIDATED_DATA_DIR / "Anomaly_Log.csv",
        index=False
    )

    print("\nValidated data saved successfully.")
    print(f"Output directory: {VALIDATED_DATA_DIR}")

# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # LOAD RAW DATA
    # ========================================================

    print("Loading raw data...")

    (
        claims,
        claim_lines,
        payments,
        authorizations,
        members,
        providers,
        plans,
        services
    ) = load_data()

    print(f"Claims loaded: {len(claims):,}")
    print(f"Claim lines loaded: {len(claim_lines):,}")
    print(f"Payments loaded: {len(payments):,}")
    print(f"Authorizations loaded: {len(authorizations):,}")

    # ========================================================
    # CREATE ANOMALY LOG
    # ========================================================

    anomaly_log = create_anomaly_log()

    # ========================================================
    # INJECT ANOMALIES
    # ========================================================

    # --------------------------------------------------------
    # 1. High-Value Claims
    # --------------------------------------------------------

    claims, anomaly_log = inject_high_value_claims(
        claims,
        anomaly_log,
        percentage=0.02
    )

    # --------------------------------------------------------
    # 2. Duplicate Claims
    # --------------------------------------------------------

    (
        claims,
        claim_lines,
        anomaly_log
    ) = inject_duplicate_claims(
        claims,
        claim_lines,
        anomaly_log,
        percentage=0.015
    )

    # --------------------------------------------------------
    # 3. Excessive Member Frequency
    # --------------------------------------------------------

    claims, anomaly_log = inject_excessive_member_frequency(
        claims,
        anomaly_log,
        percentage=0.015
    )

    # --------------------------------------------------------
    # 4. Provider Risk
    # --------------------------------------------------------

    claims, anomaly_log = inject_provider_risk(
        claims,
        providers,
        anomaly_log,
        number_of_providers=12
    )

    # --------------------------------------------------------
    # 5. Service Cost Anomalies
    # --------------------------------------------------------

    (
        claim_lines,
        anomaly_log
    ) = inject_service_cost_anomalies(
        claim_lines,
        services,
        anomaly_log,
        percentage=0.015
    )

    # --------------------------------------------------------
    # 6. Excessive Quantity Anomalies
    # --------------------------------------------------------

    (
        claim_lines,
        anomaly_log
    ) = inject_excessive_quantity(
        claim_lines,
        anomaly_log,
        percentage=0.01
    )

    # --------------------------------------------------------
    # 7. Suspicious Timing
    # --------------------------------------------------------

    claims, anomaly_log = inject_suspicious_timing(
        claims,
        anomaly_log,
        percentage=0.01
    )

    # --------------------------------------------------------
    # 8. Missing Authorization
    # --------------------------------------------------------

    (
        claims,
        claim_lines,
        authorizations,
        anomaly_log
    ) = inject_missing_authorization(
        claims,
        claim_lines,
        authorizations,
        anomaly_log,
        percentage=0.02
    )
    # --------------------------------------------------------
    # 9. Plan Coverage Issues
    # --------------------------------------------------------

    (
        claims,
        claim_lines,
        anomaly_log
    ) = inject_plan_coverage_issues(
        claims,
        claim_lines,
        members,
        plans,
        services,
        anomaly_log,
        percentage=0.01
    )

    # ========================================================
    # FINAL FINANCIAL RECONCILIATION
    # ========================================================

    claim_lines = reconcile_claim_lines(claim_lines)
    payments = reconcile_payments_to_claims(claims, payments)

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("ANOMALY INJECTION SUMMARY")
    print("=" * 60)

    print(f"Total anomalies recorded: {len(anomaly_log):,}")
    print(f"Final claims: {len(claims):,}")
    print(f"Final claim lines: {len(claim_lines):,}")
    print(f"Final payments: {len(payments):,}")
    print(f"Final authorizations: {len(authorizations):,}")
    

    # ========================================================
    # SAVE VALIDATED DATA
    # ========================================================

    save_data(
        claims,
        claim_lines,
        payments,
        authorizations,
        anomaly_log
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
