import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

from config import (
    NUM_HMOS,
    NUM_PLANS,
    NUM_MEMBERS,
    NUM_PROVIDERS,
    NUM_DIAGNOSES,
    NUM_SERVICES,
    NUM_CLAIMS,
    RAW_DATA_DIR,
    RANDOM_SEED,
    START_DATE,
    END_DATE
)


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# HMO MASTER DATA
# ============================================================

HMO_NAMES = [
    "HealthBridge HMO",
    "CareSure Health HMO",
    "PrimeHealth HMO",
    "WellLife HMO",
    "MediTrust HMO"
]

HMO_STATES = [
    "Lagos",
    "FCT",
    "Rivers",
    "Oyo",
    "Kano"
]


# ============================================================
# PLAN TYPES
# ============================================================

PLAN_TYPES = [
    "Basic",
    "Standard",
    "Premium",
    "Corporate"
]


# ============================================================
# MEMBER DATA
# ============================================================

MALE_FIRST_NAMES = [
    "Chinedu",
    "Emeka",
    "Ifeanyi",
    "Obinna",
    "Kelechi",
    "Daniel",
    "David",
    "Samuel",
    "Michael",
    "Joseph",
    "Joshua",
    "Victor",
    "Francis",
    "Benjamin",
    "Tunde"
]

FEMALE_FIRST_NAMES = [
    "Ada",
    "Amaka",
    "Chioma",
    "Ngozi",
    "Chiamaka",
    "Grace",
    "Esther",
    "Deborah",
    "Mercy",
    "Faith",
    "Jennifer",
    "Blessing",
    "Ifeoma",
    "Joy",
    "Patience"
]

LAST_NAMES = [
    "Okafor",
    "Eze",
    "Nwosu",
    "Obi",
    "Okeke",
    "Ibrahim",
    "Musa",
    "Yusuf",
    "Adeyemi",
    "Adebayo",
    "Balogun",
    "Ogunleye",
    "Ezekiel",
    "Uche",
    "Onyeka",
    "Agu",
    "Nwachukwu",
    "Ezeh",
    "Chukwu",
    "Opara"
]


LOCATION_DATA = {
    "Lagos": [
        "Lagos",
        "Ikeja",
        "Surulere",
        "Yaba",
        "Lekki",
        "Alimosho"
    ],
    "FCT": [
        "Abuja",
        "Gwagwalada",
        "Kubwa",
        "Maitama",
        "Wuse"
    ],
    "Rivers": [
        "Port Harcourt",
        "Obio-Akpor",
        "Eleme"
    ],
    "Oyo": [
        "Ibadan",
        "Ogbomosho",
        "Oyo"
    ],
    "Kano": [
        "Kano",
        "Fagge",
        "Nassarawa",
        "Dala"
    ]
}


# ============================================================
# GENERATE HMOs
# ============================================================

def generate_hmos():

    records = []

    for i in range(NUM_HMOS):

        hmo_id = f"HMO{i + 1:03d}"

        record = {
            "HMO_ID": hmo_id,
            "HMO_Name": HMO_NAMES[i],
            "HMO_Type": "Private",
            "State": HMO_STATES[i],
            "Status": "Active",
            "Contract_Start_Date": date(2022, 1, 1),
            "Contract_End_Date": date(2025, 12, 31)
        }

        records.append(record)

    return pd.DataFrame(records)


# ============================================================
# GENERATE PLANS
# ============================================================

def generate_plans():

    records = []

    plan_counter = 1

    for hmo_index in range(NUM_HMOS):

        hmo_id = f"HMO{hmo_index + 1:03d}"
        hmo_name = HMO_NAMES[hmo_index]

        for plan_type in PLAN_TYPES:

            plan_id = f"PL{plan_counter:03d}"

            if plan_type == "Basic":

                annual_limit = 500_000
                outpatient_limit = 150_000
                inpatient_limit = 350_000
                maternity_cover = 0
                dental_cover = 0
                optical_cover = 0

            elif plan_type == "Standard":

                annual_limit = 1_000_000
                outpatient_limit = 300_000
                inpatient_limit = 700_000
                maternity_cover = 1
                dental_cover = 0
                optical_cover = 1

            elif plan_type == "Premium":

                annual_limit = 2_500_000
                outpatient_limit = 750_000
                inpatient_limit = 1_750_000
                maternity_cover = 1
                dental_cover = 1
                optical_cover = 1

            else:

                annual_limit = 5_000_000
                outpatient_limit = 1_500_000
                inpatient_limit = 3_500_000
                maternity_cover = 1
                dental_cover = 1
                optical_cover = 1

            record = {
                "Plan_ID": plan_id,
                "HMO_ID": hmo_id,
                "Plan_Name": f"{hmo_name} {plan_type}",
                "Plan_Type": plan_type,
                "Annual_Limit": annual_limit,
                "Outpatient_Limit": outpatient_limit,
                "Inpatient_Limit": inpatient_limit,
                "Maternity_Cover": maternity_cover,
                "Dental_Cover": dental_cover,
                "Optical_Cover": optical_cover,
                "Plan_Status": "Active"
            }

            records.append(record)

            plan_counter += 1

    return pd.DataFrame(records)


# ============================================================
# AGE GROUP FUNCTION
# ============================================================

def get_age_group(age):

    if age <= 17:
        return "0-17"

    elif age <= 30:
        return "18-30"

    elif age <= 45:
        return "31-45"

    elif age <= 60:
        return "46-60"

    else:
        return "61+"


# ============================================================
# GENERATE MEMBERS
# ============================================================

def generate_members(plan_df):

    records = []

    # --------------------------------------------------------
    # HMO distribution
    # --------------------------------------------------------

    hmo_ids = [
        "HMO001",
        "HMO002",
        "HMO003",
        "HMO004",
        "HMO005"
    ]

    hmo_weights = [
        0.27,
        0.23,
        0.20,
        0.17,
        0.13
    ]

    # --------------------------------------------------------
    # State distribution
    # --------------------------------------------------------

    state_weights = {
        "Lagos": 0.35,
        "FCT": 0.25,
        "Rivers": 0.15,
        "Oyo": 0.15,
        "Kano": 0.10
    }

    states = list(state_weights.keys())
    weights = list(state_weights.values())

    # --------------------------------------------------------
    # Generate members
    # --------------------------------------------------------

    for i in range(NUM_MEMBERS):

        member_id = f"M{i + 1:06d}"

        # Gender
        gender = random.choices(
            ["Male", "Female"],
            weights=[0.48, 0.52],
            k=1
        )[0]

        # First name based on gender
        if gender == "Male":
            first_name = random.choice(MALE_FIRST_NAMES)
        else:
            first_name = random.choice(FEMALE_FIRST_NAMES)

        last_name = random.choice(LAST_NAMES)

        # ----------------------------------------------------
        # Date of birth
        # ----------------------------------------------------

        birth_year = random.randint(1955, 2020)

        birth_date = date(
            birth_year,
            random.randint(1, 12),
            random.randint(1, 28)
        )

        # Approximate age at end of 2025
        age = 2025 - birth_year

        age_group = get_age_group(age)

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        state = random.choices(
            states,
            weights=weights,
            k=1
        )[0]

        city = random.choice(LOCATION_DATA[state])

        # ----------------------------------------------------
        # HMO assignment
        # ----------------------------------------------------

        hmo_id = random.choices(
            hmo_ids,
            weights=hmo_weights,
            k=1
        )[0]

        # ----------------------------------------------------
        # Get plans belonging to selected HMO
        # ----------------------------------------------------

        hmo_plans = plan_df[
            plan_df["HMO_ID"] == hmo_id
        ]

        plan_id = random.choice(
            hmo_plans["Plan_ID"].tolist()
        )

        # ----------------------------------------------------
        # Enrollment date
        # ----------------------------------------------------

        enrollment_year = random.randint(2022, 2025)

        enrollment_date = date(
            enrollment_year,
            random.randint(1, 12),
            random.randint(1, 28)
        )

        # ----------------------------------------------------
        # Member status
        # ----------------------------------------------------

        member_status = random.choices(
            ["Active", "Inactive"],
            weights=[0.85, 0.15],
            k=1
        )[0]

        # ----------------------------------------------------
        # Termination date
        # ----------------------------------------------------

        if member_status == "Inactive":

            termination_date = date(
                random.randint(
                    enrollment_date.year,
                    2025
                ),
                random.randint(1, 12),
                random.randint(1, 28)
            )

            # Ensure termination isn't before enrollment
            if termination_date < enrollment_date:
                termination_date = enrollment_date

        else:

            termination_date = None

        # ----------------------------------------------------
        # Build record
        # ----------------------------------------------------

        record = {
            "Member_ID": member_id,
            "First_Name": first_name,
            "Last_Name": last_name,
            "Gender": gender,
            "Date_of_Birth": birth_date,
            "Age": age,
            "Age_Group": age_group,
            "State": state,
            "City": city,
            "Enrollment_Date": enrollment_date,
            "Termination_Date": termination_date,
            "Member_Status": member_status,
            "Plan_ID": plan_id,
            "HMO_ID": hmo_id
        }

        records.append(record)

    return pd.DataFrame(records)


 # ============================================================
# PROVIDER DATA
# ============================================================

PROVIDER_TYPES = [
    "Hospital",
    "Clinic",
    "Laboratory",
    "Pharmacy",
    "Diagnostic Centre",
    "Specialist Centre"
]

PROVIDER_TYPE_WEIGHTS = [
    45,
    30,
    15,
    12,
    10,
    8
]

PROVIDER_TIERS = [
    "Tier 1",
    "Tier 2",
    "Tier 3"
]

PROVIDER_TIER_WEIGHTS = [
    20,
    50,
    30
]

PROVIDER_STATES = [
    "Lagos",
    "FCT",
    "Rivers",
    "Oyo",
    "Kano"
]

PROVIDER_LOCATION_DATA = {
    "Lagos": [
        "Lagos",
        "Ikeja",
        "Surulere",
        "Yaba",
        "Lekki",
        "Alimosho",
        "Apapa",
        "Festac"
    ],

    "FCT": [
        "Abuja",
        "Gwarinpa",
        "Kubwa",
        "Wuse",
        "Maitama",
        "Gwagwalada"
    ],

    "Rivers": [
        "Port Harcourt",
        "Obio-Akpor",
        "Eleme"
    ],

    "Oyo": [
        "Ibadan",
        "Ogbomosho",
        "Oyo"
    ],

    "Kano": [
        "Kano",
        "Fagge",
        "Dala",
        "Nassarawa"
    ]
}

PROVIDER_PREFIXES = {
    "Hospital": [
        "General",
        "Central",
        "Metropolitan",
        "Specialist",
        "University",
        "Memorial"
    ],

    "Clinic": [
        "Family",
        "Prime",
        "Community",
        "Advanced",
        "Medicare",
        "Wellness"
    ],

    "Laboratory": [
        "Diagnostic",
        "MedLab",
        "Pathcare",
        "HealthLab",
        "Clinical"
    ],

    "Pharmacy": [
        "HealthPlus",
        "MediCare",
        "LifeCare",
        "PrimeCare",
        "Wellness"
    ],

    "Diagnostic Centre": [
        "Advanced",
        "Precision",
        "Imaging",
        "Medical"
    ],

    "Specialist Centre": [
        "Specialist",
        "Advanced",
        "Centre for"
    ]
}

PROVIDER_SUFFIXES = {
    "Hospital": "Hospital",
    "Clinic": "Clinic",
    "Laboratory": "Laboratory",
    "Pharmacy": "Pharmacy",
    "Diagnostic Centre": "Diagnostic Centre",
    "Specialist Centre": "Specialist Centre"
}


# ============================================================
# GENERATE PROVIDERS
# ============================================================

def generate_providers():

    records = []

    provider_number = 1

    for i in range(NUM_PROVIDERS):

        provider_id = f"PRV{i + 1:04d}"

        provider_type = random.choices(
            PROVIDER_TYPES,
            weights=PROVIDER_TYPE_WEIGHTS,
            k=1
        )[0]

        state = random.choices(
            PROVIDER_STATES,
            weights=[
                0.35,
                0.25,
                0.15,
                0.15,
                0.10
            ],
            k=1
        )[0]

        city = random.choice(
            PROVIDER_LOCATION_DATA[state]
        )

        provider_tier = random.choices(
            PROVIDER_TIERS,
            weights=PROVIDER_TIER_WEIGHTS,
            k=1
        )[0]

        accreditation_status = random.choices(
            [
                "Accredited",
                "Pending",
                "Expired"
            ],
            weights=[
                0.85,
                0.10,
                0.05
            ],
            k=1
        )[0]

        provider_prefix = random.choice(
            PROVIDER_PREFIXES[provider_type]
        )

        provider_name = (
            f"{provider_prefix} "
            f"{city} "
            f"{PROVIDER_SUFFIXES[provider_type]}"
        )

        contract_start_year = random.randint(
            2022,
            2024
        )

        contract_start_date = date(
            contract_start_year,
            random.randint(1, 12),
            random.randint(1, 28)
        )

        contract_end_date = date(
            2025,
            12,
            31
        )

        provider_status = random.choices(
            [
                "Active",
                "Inactive"
            ],
            weights=[
                0.90,
                0.10
            ],
            k=1
        )[0]

        record = {
            "Provider_ID": provider_id,
            "Provider_Name": provider_name,
            "Provider_Type": provider_type,
            "State": state,
            "City": city,
            "Provider_Tier": provider_tier,
            "Accreditation_Status": accreditation_status,
            "Contract_Start_Date": contract_start_date,
            "Contract_End_Date": contract_end_date,
            "Provider_Status": provider_status
        }

        records.append(record)

        provider_number += 1

    return pd.DataFrame(records)

# ============================================================
# DIAGNOSIS MASTER DATA
# ============================================================

DIAGNOSIS_DATA = [

    ("D001", "J10", "Influenza", "Respiratory Infection", 0),
    ("D002", "J18", "Pneumonia", "Respiratory Infection", 0),
    ("D003", "J45", "Asthma", "Respiratory Infection", 1),
    ("D004", "J06", "Upper Respiratory Infection", "Respiratory Infection", 0),
    ("D005", "J00", "Common Cold", "Respiratory Infection", 0),

    ("D006", "B50", "Malaria", "Infectious Disease", 0),
    ("D007", "A01", "Typhoid Fever", "Infectious Disease", 0),
    ("D008", "A09", "Gastroenteritis", "Infectious Disease", 0),
    ("D009", "A90", "Dengue Fever", "Infectious Disease", 0),
    ("D010", "B34", "Viral Infection", "Infectious Disease", 0),

    ("D011", "I10", "Hypertension", "Cardiovascular", 1),
    ("D012", "I25", "Ischemic Heart Disease", "Cardiovascular", 1),
    ("D013", "I50", "Heart Failure", "Cardiovascular", 1),
    ("D014", "I48", "Atrial Fibrillation", "Cardiovascular", 1),

    ("D015", "E11", "Type 2 Diabetes", "Endocrine", 1),
    ("D016", "E10", "Type 1 Diabetes", "Endocrine", 1),
    ("D017", "E78", "Hyperlipidemia", "Endocrine", 1),
    ("D018", "E03", "Hypothyroidism", "Endocrine", 1),

    ("D019", "K21", "Gastroesophageal Reflux Disease", "Gastrointestinal", 1),
    ("D020", "K29", "Gastritis", "Gastrointestinal", 0),
    ("D021", "K80", "Gallstones", "Gastrointestinal", 0),
    ("D022", "K35", "Appendicitis", "Gastrointestinal", 0),

    ("D023", "N39", "Urinary Tract Infection", "Genitourinary", 0),
    ("D024", "N18", "Chronic Kidney Disease", "Genitourinary", 1),
    ("D025", "N20", "Kidney Stones", "Genitourinary", 0),

    ("D026", "M54", "Low Back Pain", "Musculoskeletal", 0),
    ("D027", "M17", "Osteoarthritis of Knee", "Musculoskeletal", 1),
    ("D028", "M81", "Osteoporosis", "Musculoskeletal", 1),

    ("D029", "L20", "Atopic Dermatitis", "Dermatological", 1),
    ("D030", "L30", "Dermatitis", "Dermatological", 0),

    ("D031", "H10", "Conjunctivitis", "Ophthalmic", 0),
    ("D032", "H25", "Cataract", "Ophthalmic", 0),

    ("D033", "F32", "Depressive Disorder", "Mental Health", 1),
    ("D034", "G43", "Migraine", "Neurological", 1),

    ("D035", "Z00", "Routine Medical Examination", "Preventive Care", 0)
]


# ============================================================
# GENERATE DIAGNOSES
# ============================================================

def generate_diagnoses():

    records = []

    for diagnosis_id, code, name, category, chronic_flag in DIAGNOSIS_DATA:

        record = {
            "Diagnosis_ID": diagnosis_id,
            "Diagnosis_Code": code,
            "Diagnosis_Name": name,
            "Disease_Category": category,
            "Chronic_Flag": chronic_flag
        }

        records.append(record)

    diagnosis_df = pd.DataFrame(records)

    return diagnosis_df
# ============================================================
# SERVICE MASTER DATA
# ============================================================

SERVICE_DATA = [

    # --------------------------------------------------------
    # CONSULTATION
    # --------------------------------------------------------

    ("S001", "General Consultation", "Consultation",
     "Outpatient", 5000, 0),

    ("S002", "Specialist Consultation", "Consultation",
     "Outpatient", 10000, 0),

    ("S003", "Emergency Consultation", "Emergency",
     "Outpatient", 15000, 0),

    ("S004", "Follow-up Consultation", "Consultation",
     "Outpatient", 4000, 0),

    # --------------------------------------------------------
    # LABORATORY
    # --------------------------------------------------------

    ("S005", "Malaria Test", "Laboratory",
     "Outpatient", 3000, 0),

    ("S006", "Full Blood Count", "Laboratory",
     "Outpatient", 5000, 0),

    ("S007", "Urinalysis", "Laboratory",
     "Outpatient", 3000, 0),

    ("S008", "Blood Chemistry", "Laboratory",
     "Outpatient", 8000, 0),

    ("S009", "Liver Function Test", "Laboratory",
     "Outpatient", 10000, 0),

    ("S010", "Kidney Function Test", "Laboratory",
     "Outpatient", 10000, 0),

    # --------------------------------------------------------
    # DIAGNOSTIC IMAGING
    # --------------------------------------------------------

    ("S011", "X-Ray", "Diagnostic Imaging",
     "Outpatient", 12000, 0),

    ("S012", "Ultrasound", "Diagnostic Imaging",
     "Outpatient", 15000, 0),

    ("S013", "ECG", "Diagnostic Imaging",
     "Outpatient", 10000, 0),

    ("S014", "CT Scan", "Diagnostic Imaging",
     "Outpatient", 80000, 1),

    ("S015", "MRI Scan", "Diagnostic Imaging",
     "Outpatient", 150000, 1),

    # --------------------------------------------------------
    # INPATIENT
    # --------------------------------------------------------

    ("S016", "Hospital Admission", "Inpatient",
     "Inpatient", 50000, 1),

    ("S017", "Inpatient Room Charge", "Inpatient",
     "Inpatient", 25000, 1),

    ("S018", "Nursing Care", "Inpatient",
     "Inpatient", 10000, 0),

    ("S019", "Wound Dressing", "Inpatient",
     "Inpatient", 8000, 0),

    # --------------------------------------------------------
    # SURGERY
    # --------------------------------------------------------

    ("S020", "Minor Surgery", "Surgery",
     "Inpatient", 100000, 1),

    ("S021", "Major Surgery", "Surgery",
     "Inpatient", 500000, 1),

    ("S022", "Caesarean Section", "Maternity",
     "Inpatient", 350000, 1),

    # --------------------------------------------------------
    # PHARMACY
    # --------------------------------------------------------

    ("S023", "Prescription Medication", "Pharmacy",
     "Outpatient", 10000, 0),

    ("S024", "Specialty Medication", "Pharmacy",
     "Outpatient", 50000, 1),

    # --------------------------------------------------------
    # REHABILITATION
    # --------------------------------------------------------

    ("S025", "Physiotherapy Session", "Rehabilitation",
     "Outpatient", 10000, 0),

    # --------------------------------------------------------
    # DENTAL
    # --------------------------------------------------------

    ("S026", "Dental Consultation", "Dental",
     "Outpatient", 8000, 0),

    ("S027", "Dental Extraction", "Dental",
     "Outpatient", 25000, 1),

    # --------------------------------------------------------
    # OPTICAL
    # --------------------------------------------------------

    ("S028", "Eye Examination", "Optical",
     "Outpatient", 8000, 0),

    ("S029", "Prescription Glasses", "Optical",
     "Outpatient", 30000, 1),

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    ("S030", "Medical Examination", "Preventive Care",
     "Outpatient", 7000, 0)
]


# ============================================================
# GENERATE SERVICES
# ============================================================

def generate_services():

    records = []

    for service_id, service_name, category, setting, cost, authorization in SERVICE_DATA:

        record = {
            "Service_ID": service_id,
            "Service_Name": service_name,
            "Service_Category": category,
            "Inpatient_Outpatient": setting,
            "Standard_Unit_Cost": cost,
            "Requires_Authorization": authorization,
            "Service_Status": "Active"
        }

        records.append(record)

    service_df = pd.DataFrame(records)

    return service_df
# ============================================================
# GENERATE DATE DIMENSION
# ============================================================

def generate_date_dimension():

    date_range = pd.date_range(
        start="2022-01-01",
        end="2025-12-31",
        freq="D"
    )

    records = []

    for current_date in date_range:

        full_date = current_date.date()

        record = {
            "Date_Key": int(
                current_date.strftime("%Y%m%d")
            ),

            "Full_Date": full_date,

            "Day": current_date.day,

            "Month": current_date.month,

            "Month_Name": current_date.strftime("%B"),

            "Quarter": current_date.quarter,

            "Year": current_date.year,

            "Week_Number": current_date.isocalendar().week,

            "Day_Name": current_date.strftime("%A"),

            "Is_Weekend": int(
                current_date.weekday() >= 5
            )
        }

        records.append(record)

    date_df = pd.DataFrame(records)

    return date_df

# ============================================================
# CLAIM CONFIGURATION
# ============================================================

CLAIM_STATUSES = [
    "Approved",
    "Partially Approved",
    "Rejected",
    "Pending"
]

CLAIM_STATUS_WEIGHTS = [
    0.68,
    0.12,
    0.12,
    0.08
]

CLAIM_TYPES = [
    "Outpatient",
    "Inpatient"
]

CLAIM_TYPE_WEIGHTS = [
    0.75,
    0.25
]


# ============================================================
# CLAIM AMOUNT GENERATOR
# ============================================================

def generate_claim_amount():

    category = random.choices(
        [
            "Low",
            "Medium",
            "High",
            "Very High",
            "Extreme"
        ],
        weights=[
            0.30,
            0.40,
            0.20,
            0.08,
            0.02
        ],
        k=1
    )[0]

    if category == "Low":
        amount = random.uniform(
            5000,
            25000
        )

    elif category == "Medium":
        amount = random.uniform(
            25000,
            100000
        )

    elif category == "High":
        amount = random.uniform(
            100000,
            250000
        )

    elif category == "Very High":
        amount = random.uniform(
            250000,
            500000
        )

    else:
        amount = random.uniform(
            500000,
            1500000
        )

    return round(amount, 2)


# ============================================================
# GENERATE CLAIMS
# ============================================================

def generate_claims(
    member_df,
    provider_df,
    diagnosis_df,
    plan_df,
    date_df
):

    records = []

    # --------------------------------------------------------
    # Prepare lookup dictionaries
    # --------------------------------------------------------

    member_records = member_df.to_dict(
        "records"
    )

    provider_ids = provider_df[
        "Provider_ID"
    ].tolist()

    diagnosis_ids = diagnosis_df[
        "Diagnosis_ID"
    ].tolist()

    plan_hmo_map = (
        plan_df
        .set_index("Plan_ID")["HMO_ID"]
        .to_dict()
    )

    date_values = pd.to_datetime(
        date_df["Full_Date"]
    ).dt.date.tolist()

    # --------------------------------------------------------
    # Generate claims
    # --------------------------------------------------------

    for i in range(NUM_CLAIMS):

        claim_id = f"CLM{i + 1:07d}"

        # ----------------------------------------------------
        # Select member
        # ----------------------------------------------------

        member = random.choice(
            member_records
        )

        member_id = member["Member_ID"]

        plan_id = member["Plan_ID"]

        hmo_id = plan_hmo_map[plan_id]

        # ----------------------------------------------------
        # Select provider and diagnosis
        # ----------------------------------------------------

        provider_id = random.choice(
            provider_ids
        )

        diagnosis_id = random.choice(
            diagnosis_ids
        )

        # ----------------------------------------------------
        # Claim type
        # ----------------------------------------------------

        claim_type = random.choices(
            CLAIM_TYPES,
            weights=CLAIM_TYPE_WEIGHTS,
            k=1
        )[0]

        # ----------------------------------------------------
        # Claim date
        # ----------------------------------------------------

        claim_date = random.choice(
            date_values
        )

        # Make sure the claim is not before enrollment
        enrollment_date = pd.to_datetime(
            member["Enrollment_Date"]
        ).date()

        if claim_date < enrollment_date:
            claim_date = enrollment_date

        # Make sure claim does not occur after termination
        if pd.notna(
            member["Termination_Date"]
        ):

            termination_date = pd.to_datetime(
                member["Termination_Date"]
            ).date()

            if claim_date > termination_date:
                claim_date = termination_date

        # ----------------------------------------------------
        # Admission / discharge
        # ----------------------------------------------------

        if claim_type == "Inpatient":

            admission_date = claim_date

            length_of_stay = random.choices(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    7,
                    10,
                    14
                ],
                weights=[
                    0.20,
                    0.20,
                    0.18,
                    0.15,
                    0.10,
                    0.08,
                    0.06,
                    0.03
                ],
                k=1
            )[0]

            discharge_date = (
                admission_date
                + timedelta(
                    days=length_of_stay
                )
            )

            # Don't allow discharge beyond project period
            end_date = pd.to_datetime(
                END_DATE
            ).date()

            if discharge_date > end_date:
                discharge_date = end_date

                length_of_stay = (
                    discharge_date
                    - admission_date
                ).days

        else:

            admission_date = None
            discharge_date = None
            length_of_stay = 0

        # ----------------------------------------------------
        # Claim amount
        # ----------------------------------------------------

        claim_amount = generate_claim_amount()

        # ----------------------------------------------------
        # Claim status
        # ----------------------------------------------------

        claim_status = random.choices(
            CLAIM_STATUSES,
            weights=CLAIM_STATUS_WEIGHTS,
            k=1
        )[0]

        # ----------------------------------------------------
        # Approved / rejected amounts
        # ----------------------------------------------------

        if claim_status == "Approved":

            approved_amount = claim_amount
            rejected_amount = 0

        elif claim_status == "Rejected":

            approved_amount = 0
            rejected_amount = claim_amount

        elif claim_status == "Partially Approved":

            approval_ratio = random.uniform(
                0.40,
                0.90
            )

            approved_amount = round(
                claim_amount
                * approval_ratio,
                2
            )

            rejected_amount = round(
                claim_amount
                - approved_amount,
                2
            )

        else:

            approved_amount = 0
            rejected_amount = 0

        # ----------------------------------------------------
        # Member copay
        # ----------------------------------------------------

        if approved_amount > 0:

            copay_rate = random.uniform(
                0.00,
                0.20
            )

            member_copay = round(
                approved_amount
                * copay_rate,
                2
            )

        else:

            member_copay = 0

        # ----------------------------------------------------
        # Submission date
        # ----------------------------------------------------

        submission_delay = random.randint(
            0,
            7
        )

        submission_date = (
            claim_date
            + timedelta(
                days=submission_delay
            )
        )

        # ----------------------------------------------------
        # Processing date
        # ----------------------------------------------------

        if claim_status == "Pending":

            processing_date = None

        else:

            processing_delay = random.randint(
                1,
                14
            )

            processing_date = (
                submission_date
                + timedelta(
                    days=processing_delay
                )
            )

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------

        record = {

            "Claim_ID": claim_id,

            "Member_ID": member_id,

            "Provider_ID": provider_id,

            "HMO_ID": hmo_id,

            "Plan_ID": plan_id,

            "Diagnosis_ID": diagnosis_id,

            "Claim_Date": claim_date,

            "Admission_Date": admission_date,

            "Discharge_Date": discharge_date,

            "Authorization_ID": None,

            "Claim_Type": claim_type,

            "Claim_Status": claim_status,

            "Claim_Amount": claim_amount,

            "Approved_Amount": approved_amount,

            "Rejected_Amount": rejected_amount,

            "Member_Copay": member_copay,

            "Length_of_Stay": length_of_stay,

            "Submission_Date": submission_date,

            "Processing_Date": processing_date
        }

        records.append(record)

    return pd.DataFrame(records)
# ============================================================
# CLAIM LINE CONFIGURATION
# ============================================================

AUTHORIZATION_STATUSES = [
    "Approved",
    "Pending",
    "Missing"
]

AUTHORIZATION_STATUS_WEIGHTS = [
    0.80,
    0.10,
    0.10
]

# ============================================================
# GENERATE CLAIM LINES
# ============================================================

def generate_claim_lines(
    claim_df,
    service_df
):

    records = []

    # --------------------------------------------------------
    # Prepare service records
    # --------------------------------------------------------

    service_records = service_df.to_dict(
        "records"
    )

    outpatient_services = [
        service
        for service in service_records
        if service["Inpatient_Outpatient"]
        == "Outpatient"
    ]

    inpatient_services = [
        service
        for service in service_records
        if service["Inpatient_Outpatient"]
        == "Inpatient"
    ]

    # --------------------------------------------------------
    # Process every claim
    # --------------------------------------------------------

    claim_line_counter = 1

    for _, claim in claim_df.iterrows():

        claim_id = claim["Claim_ID"]

        claim_amount = float(
            claim["Claim_Amount"]
        )

        approved_amount = float(
            claim["Approved_Amount"]
        )

        rejected_amount = float(
            claim["Rejected_Amount"]
        )

        claim_type = claim["Claim_Type"]

        # ----------------------------------------------------
        # Determine number of services
        # ----------------------------------------------------

        number_of_lines = random.choices(
            [1, 2, 3, 4],
            weights=[
                0.10,
                0.45,
                0.35,
                0.10
            ],
            k=1
        )[0]

        # ----------------------------------------------------
        # Select appropriate service pool
        # ----------------------------------------------------

        if claim_type == "Inpatient":

            service_pool = inpatient_services

        else:

            service_pool = outpatient_services

        selected_services = random.sample(
            service_pool,
            min(
                number_of_lines,
                len(service_pool)
            )
        )

        # ----------------------------------------------------
        # Create estimated weights
        # ----------------------------------------------------

        line_weights = []

        for service in selected_services:

            standard_cost = float(
                service["Standard_Unit_Cost"]
            )

            quantity = random.choices(
                [1, 2, 3],
                weights=[
                    0.85,
                    0.12,
                    0.03
                ],
                k=1
            )[0]

            cost_variation = random.uniform(
                0.90,
                1.15
            )

            estimated_amount = (
                standard_cost
                * quantity
                * cost_variation
            )

            line_weights.append(
                {
                    "service": service,
                    "quantity": quantity,
                    "estimated_amount": estimated_amount
                }
            )

        # ----------------------------------------------------
        # Total estimated value
        # ----------------------------------------------------

        total_weight = sum(
            item["estimated_amount"]
            for item in line_weights
        )

        # ----------------------------------------------------
        # Create claim lines
        # ----------------------------------------------------

        allocated_amount = 0
        allocated_approved = 0
        allocated_rejected = 0

        for index, item in enumerate(
            line_weights
        ):

            service = item["service"]

            quantity = item["quantity"]

            # ------------------------------------------------
            # Allocate claim amount across lines
            # ------------------------------------------------

            if index == len(line_weights) - 1:

                line_amount = round(
                    claim_amount
                    - allocated_amount,
                    2
                )

            else:

                allocation_ratio = (
                    item["estimated_amount"]
                    / total_weight
                )

                line_amount = round(
                    claim_amount
                    * allocation_ratio,
                    2
                )

            # allocated_amount is updated after Unit_Cost rounding below.

            # ------------------------------------------------
            # Allocate approved amount
            # ------------------------------------------------

            if index == len(line_weights) - 1:

                approved_line_amount = round(
                    approved_amount
                    - allocated_approved,
                    2
                )

            else:

                approval_ratio = (
                    approved_amount
                    / claim_amount
                    if claim_amount > 0
                    else 0
                )

                approved_line_amount = round(
                    line_amount
                    * approval_ratio,
                    2
                )

            allocated_approved += (
                approved_line_amount
            )

            # ------------------------------------------------
            # Allocate rejected amount
            # ------------------------------------------------

            if index == len(line_weights) - 1:

                rejected_line_amount = round(
                    rejected_amount
                    - allocated_rejected,
                    2
                )

            else:

                rejection_ratio = (
                    rejected_amount
                    / claim_amount
                    if claim_amount > 0
                    else 0
                )

                rejected_line_amount = round(
                    line_amount
                    * rejection_ratio,
                    2
                )

            allocated_rejected += (
                rejected_line_amount
            )

            # ------------------------------------------------
            # Calculate unit cost and preserve arithmetic integrity
            # ------------------------------------------------

            # Unit_Cost is stored to 2 decimal places, so Line_Amount
            # must be derived from the stored Unit_Cost. This prevents
            # rounding mismatches such as Quantity * Unit_Cost != Line_Amount.
            unit_cost = round(
                line_amount / quantity,
                2
            )

            line_amount = round(
                unit_cost * quantity,
                2
            )

            allocated_amount += line_amount

            # ------------------------------------------------
            # Authorization
            # ------------------------------------------------

            authorization_required = int(
                service["Requires_Authorization"]
            )

            if authorization_required == 1:

                authorization_status = random.choices(
                    AUTHORIZATION_STATUSES,
                    weights=AUTHORIZATION_STATUS_WEIGHTS,
                    k=1
                )[0]

            else:

                authorization_status = "Not Required"

            # ------------------------------------------------
            # Create record
            # ------------------------------------------------

            record = {

                "Claim_Line_ID":
                    f"CL{claim_line_counter:09d}",

                "Claim_ID":
                    claim_id,

                "Service_ID":
                    service["Service_ID"],

                "Quantity":
                    quantity,

                "Unit_Cost":
                    unit_cost,

                "Line_Amount":
                    line_amount,

                "Approved_Line_Amount":
                    approved_line_amount,

                "Rejected_Line_Amount":
                    rejected_line_amount,

                "Authorization_Required":
                    authorization_required,

                "Authorization_Status":
                    authorization_status
            }

            records.append(
                record
            )

            claim_line_counter += 1

    # --------------------------------------------------------
    # Return claim-line dataframe
    # --------------------------------------------------------

    return pd.DataFrame(
        records
    )
# ============================================================
# PAYMENT CONFIGURATION
# ============================================================

PAYMENT_STATUSES = [
    "Paid",
    "Partially Paid",
    "Failed",
    "Reversed"
]

PAYMENT_STATUS_WEIGHTS = [
    0.84,
    0.08,
    0.05,
    0.03
]

PAYMENT_METHODS = [
    "Bank Transfer",
    "Electronic Transfer",
    "Direct Credit"
]

PAYMENT_METHOD_WEIGHTS = [
    0.60,
    0.25,
    0.15
]
# ============================================================
# GENERATE PAYMENTS
# ============================================================

def generate_payments(claim_df):

    records = []

    payment_counter = 1

    # --------------------------------------------------------
    # Process claims with an approved amount
    # --------------------------------------------------------

    for _, claim in claim_df.iterrows():

        approved_amount = float(
            claim["Approved_Amount"]
        )

        # ----------------------------------------------------
        # No approved amount = no payment transaction
        # ----------------------------------------------------

        if approved_amount <= 0:
            continue

        # ----------------------------------------------------
        # Some approved claims remain unpaid
        #
        # This helps us create outstanding balances.
        # Approximately 10% of payable claims remain unpaid.
        # ----------------------------------------------------

        payment_created = random.random() < 0.90

        if not payment_created:
            continue

        claim_id = claim["Claim_ID"]

        processing_date = claim["Processing_Date"]

        if pd.isna(processing_date):
            continue

        processing_date = pd.to_datetime(
            processing_date
        ).date()

        # ----------------------------------------------------
        # Payment date
        # ----------------------------------------------------

        payment_delay = random.randint(
            1,
            30
        )

        payment_date = (
            processing_date
            + timedelta(
                days=payment_delay
            )
        )

        # ----------------------------------------------------
        # Keep payment within project period
        # ----------------------------------------------------

        project_end_date = pd.to_datetime(
            END_DATE
        ).date()

        if payment_date > project_end_date:
            payment_date = project_end_date

        # ----------------------------------------------------
        # Payment status
        # ----------------------------------------------------

        payment_status = random.choices(
            PAYMENT_STATUSES,
            weights=PAYMENT_STATUS_WEIGHTS,
            k=1
        )[0]

        # ----------------------------------------------------
        # Payment amount
        # ----------------------------------------------------

        if payment_status == "Paid":

            payment_ratio = random.uniform(
                0.95,
                1.00
            )

            payment_amount = round(
                approved_amount
                * payment_ratio,
                2
            )

        elif payment_status == "Partially Paid":

            payment_ratio = random.uniform(
                0.30,
                0.80
            )

            payment_amount = round(
                approved_amount
                * payment_ratio,
                2
            )

        elif payment_status == "Reversed":

            payment_ratio = random.uniform(
                0.80,
                1.00
            )

            payment_amount = round(
                approved_amount
                * payment_ratio,
                2
            )

        else:
            # Failed payment
            payment_amount = 0

        # ----------------------------------------------------
        # Payment method
        # ----------------------------------------------------

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=PAYMENT_METHOD_WEIGHTS,
            k=1
        )[0]

        # ----------------------------------------------------
        # Payment batch
        # ----------------------------------------------------

        payment_batch = (
            f"PB"
            f"{payment_date.strftime('%Y%m')}"
            f"{random.randint(1, 50):02d}"
        )

        # ----------------------------------------------------
        # Payment reference
        # ----------------------------------------------------

        payment_reference = (
            f"PAY{payment_counter:09d}"
        )

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------

        record = {

            "Payment_ID":
                f"PMT{payment_counter:09d}",

            "Claim_ID":
                claim_id,

            "Payment_Date":
                payment_date,

            "Payment_Reference":
                payment_reference,

            "Payment_Amount":
                payment_amount,

            "Payment_Status":
                payment_status,

            "Payment_Method":
                payment_method,

            "Payment_Batch":
                payment_batch
        }

        records.append(record)

        payment_counter += 1

    return pd.DataFrame(records)
# ============================================================
# AUTHORIZATION CONFIGURATION
# ============================================================

AUTHORIZATION_STATUSES = [
    "Approved",
    "Pending",
    "Rejected",
    "Expired"
]

AUTHORIZATION_STATUS_WEIGHTS = [
    0.85,
    0.08,
    0.05,
    0.02
]
# ============================================================
# GENERATE AUTHORIZATIONS
# ============================================================

def generate_authorizations(
    claim_df,
    claim_line_df,
    member_df,
    provider_df,
    diagnosis_df,
    service_df
):

    records = []

    authorization_counter = 1

    # --------------------------------------------------------
    # Identify services that require authorization
    # --------------------------------------------------------

    authorization_services = set(
        service_df.loc[
            service_df["Requires_Authorization"] == 1,
            "Service_ID"
        ]
    )

    # --------------------------------------------------------
    # Find claim lines requiring authorization
    # --------------------------------------------------------

    eligible_lines = claim_line_df[
        claim_line_df["Service_ID"].isin(
            authorization_services
        )
    ].copy()

    # --------------------------------------------------------
    # Attach claim information
    # --------------------------------------------------------

    eligible_lines = eligible_lines.merge(
        claim_df[
            [
                "Claim_ID",
                "Member_ID",
                "Provider_ID",
                "HMO_ID",
                "Plan_ID",
                "Diagnosis_ID",
                "Claim_Date",
                "Claim_Status"
            ]
        ],
        on="Claim_ID",
        how="left"
    )

    # --------------------------------------------------------
    # One authorization request per claim
    #
    # If a claim has multiple authorization-required
    # services, choose one representative service.
    # --------------------------------------------------------

    eligible_lines = (
        eligible_lines
        .groupby("Claim_ID", as_index=False)
        .first()
    )

    # --------------------------------------------------------
    # Deliberately leave approximately 2% without
    # authorization records.
    #
    # These will later support Missing Authorization risk.
    # --------------------------------------------------------

    for _, row in eligible_lines.iterrows():

        create_authorization = (
            random.random() >= 0.02
        )

        if not create_authorization:
            continue

        claim_date = pd.to_datetime(
            row["Claim_Date"]
        ).date()

        # ----------------------------------------------------
        # Request date
        # ----------------------------------------------------

        request_days_before = random.randint(
            0,
            3
        )

        request_date = (
            claim_date
            - timedelta(
                days=request_days_before
            )
        )

        project_start_date = pd.to_datetime(
            START_DATE
        ).date()

        if request_date < project_start_date:
            request_date = project_start_date

        # ----------------------------------------------------
        # Authorization status
        # ----------------------------------------------------

        authorization_status = random.choices(
            AUTHORIZATION_STATUSES,
            weights=AUTHORIZATION_STATUS_WEIGHTS,
            k=1
        )[0]

        # ----------------------------------------------------
        # Requested amount
        # ----------------------------------------------------

        requested_amount = round(
            float(row["Line_Amount"]),
            2
        )

        # ----------------------------------------------------
        # Approved amount
        # ----------------------------------------------------

        if authorization_status == "Approved":

            approval_ratio = random.uniform(
                0.80,
                1.00
            )

            authorization_approved_amount = round(
                requested_amount
                * approval_ratio,
                2
            )

        elif authorization_status == "Rejected":

            authorization_approved_amount = 0

        elif authorization_status == "Pending":

            authorization_approved_amount = 0

        else:
            # Expired
            authorization_approved_amount = round(
                requested_amount
                * random.uniform(
                    0.50,
                    0.90
                ),
                2
            )

        # ----------------------------------------------------
        # Approval date
        # ----------------------------------------------------

        if authorization_status == "Pending":

            approval_date = None

        else:

            approval_delay = random.randint(
                0,
                3
            )

            approval_date = (
                request_date
                + timedelta(
                    days=approval_delay
                )
            )

            # Approval should not be after the claim date
            if approval_date > claim_date:
                approval_date = claim_date

        # ----------------------------------------------------
        # Authorization validity
        # ----------------------------------------------------

        valid_from = request_date

        valid_to = (
            claim_date
            + timedelta(
                days=random.randint(
                    7,
                    30
                )
            )
        )

        # ----------------------------------------------------
        # Authorization ID
        # ----------------------------------------------------

        authorization_id = (
            f"AUTH{authorization_counter:09d}"
        )

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------
        record = {

            "Authorization_ID":
                authorization_id,

            "Claim_ID":
                row["Claim_ID"],

            "Member_ID":
                row["Member_ID"],

            "Provider_ID":
                row["Provider_ID"],

            "Service_ID":
                row["Service_ID"],

            "Diagnosis_ID":
                row["Diagnosis_ID"],

            "Request_Date":
                request_date,

            "Approval_Date":
                approval_date,

            "Requested_Amount":
                requested_amount,

            "Approved_Amount":
                authorization_approved_amount,

            "Authorization_Status":
                authorization_status,

            "Valid_From":
                valid_from,

            "Valid_To":
                valid_to
        }

        records.append(record)

        authorization_counter += 1

    authorization_df = pd.DataFrame(
        records
    )

    return authorization_df
# ============================================================
# SAVE AUTHORIZATIONS
# ============================================================

def save_authorizations(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        RAW_DATA_DIR
        / "Fact_Authorizations.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Authorization data saved to: "
        f"{output_file}"
    )
# ============================================================
# SAVE DATA
# ============================================================

def save_hmos(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_HMO.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"HMO data saved to: {output_file}"
    )


def save_plans(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Plan.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Plan data saved to: {output_file}"
    )


def save_members(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Member.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Member data saved to: {output_file}"
    )
def save_providers(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Provider.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Provider data saved to: {output_file}"
    )
    # ============================================================
# SAVE DIAGNOSES
# ============================================================

def save_diagnoses(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Diagnosis.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Diagnosis data saved to: {output_file}"
    )
# ============================================================
# SAVE SERVICES
# ============================================================

def save_services(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Service.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Service data saved to: {output_file}"
    )
    # ============================================================
# SAVE DATE DIMENSION
# ============================================================

def save_date_dimension(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Dim_Date.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Date dimension saved to: {output_file}"
    )

    # ============================================================
# SAVE CLAIMS
# ============================================================

def save_claims(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "Fact_Claims.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Claims data saved to: {output_file}"
    )
    # ============================================================
# SAVE CLAIM LINES
# ============================================================

def save_claim_lines(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        RAW_DATA_DIR
        / "Fact_Claim_Lines.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Claim line data saved to: "
        f"{output_file}"
    )
    # ============================================================
# SAVE PAYMENTS
# ============================================================

def save_payments(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        RAW_DATA_DIR
        / "Fact_Payments.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Payment data saved to: "
        f"{output_file}"
    )
    # ============================================================
# SAVE AUTHORIZATIONS
# ============================================================

def save_authorizations(df):

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        RAW_DATA_DIR
        / "Fact_Authorizations.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Authorization data saved to: "
        f"{output_file}"
    )
# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # GENERATE DIMENSIONS
    # --------------------------------------------------------

    hmo_df = generate_hmos()

    plan_df = generate_plans()

    member_df = generate_members(
        plan_df
    )

    provider_df = generate_providers()

    diagnosis_df = generate_diagnoses()

    service_df = generate_services()

    date_df = generate_date_dimension()

    # --------------------------------------------------------
    # GENERATE FACT TABLE
    # --------------------------------------------------------

    claim_df = generate_claims(
        member_df,
        provider_df,
        diagnosis_df,
        plan_df,
        date_df
    )
    claim_line_df = generate_claim_lines(
    claim_df,
    service_df
)
    payment_df = generate_payments(
    claim_df
)
        # --------------------------------------------------------
    # GENERATE AUTHORIZATIONS
    # --------------------------------------------------------

    authorization_df = generate_authorizations(
        claim_df,
        claim_line_df,
        member_df,
        provider_df,
        diagnosis_df,
        service_df
    )

    # --------------------------------------------------------
    # LINK AUTHORIZATIONS TO CLAIMS
    # --------------------------------------------------------

    authorization_map = dict(
        zip(
            authorization_df["Claim_ID"],
            authorization_df["Authorization_ID"]
        )
    )

    claim_df["Authorization_ID"] = (
        claim_df["Claim_ID"].map(
            authorization_map
        )
    )
    # --------------------------------------------------------
    # SAVE DIMENSIONS
    # --------------------------------------------------------

    save_hmos(hmo_df)

    save_plans(plan_df)

    save_members(member_df)

    save_providers(provider_df)

    save_diagnoses(diagnosis_df)

    save_services(service_df)

    save_date_dimension(date_df)

  # --------------------------------------------------------
# SAVE FACT TABLES
# --------------------------------------------------------

    save_claims(claim_df)

    save_claim_lines(claim_line_df)

    save_payments(
    payment_df
)

    save_authorizations(
    authorization_df
)
    # --------------------------------------------------------
    # GENERATION SUMMARY
    # --------------------------------------------------------

    print()
    print("==========================================")
    print("GENERATION SUMMARY")
    print("==========================================")

    print(f"HMOs:       {len(hmo_df)}")
    print(f"Plans:      {len(plan_df)}")
    print(f"Members:    {len(member_df)}")
    print(f"Providers:  {len(provider_df)}")
    print(f"Diagnoses:  {len(diagnosis_df)}")
    print(f"Services:   {len(service_df)}")
    print(f"Dates:      {len(date_df)}")
    print(f"Claims:     {len(claim_df)}")
    print(
    f"Claim Lines: {len(claim_line_df)}"
)
    print(
    f"Payments:    {len(payment_df)}"
)
   
    

    # --------------------------------------------------------
    # SAMPLE DATE DATA
    # --------------------------------------------------------

    print()
    print("==========================================")
    print("DATE SAMPLE")
    print("==========================================")

    print(date_df.head(10))

    # --------------------------------------------------------
    # SAMPLE CLAIM DATA
    # --------------------------------------------------------

    print()
    print("==========================================")
    print("CLAIM GENERATION")
    print("==========================================")

    print(f"Number of Claims: {len(claim_df)}")

    print()
    print(claim_df.head(10))
    print()
    print("==========================================")
    print("CLAIM LINE GENERATION")
    print("==========================================")

    print(
    f"Number of Claim Lines: "
    f"{len(claim_line_df)}"
)

    print()
    print(
    claim_line_df.head(10)
)
    print()
    print("==========================================")
    print("PAYMENT GENERATION")
    print("==========================================")

    print(
    f"Number of Payments: "
    f"{len(payment_df)}"
)

    print()
    print(
    payment_df.head(10)
)
    # --------------------------------------------------------
    # GENERATION SUMMARY
    # --------------------------------------------------------

    print()
    print("==========================================")
    print("GENERATION SUMMARY")
    print("==========================================")

    print(f"HMOs:             {len(hmo_df)}")
    print(f"Plans:            {len(plan_df)}")
    print(f"Members:          {len(member_df)}")
    print(f"Providers:        {len(provider_df)}")
    print(f"Diagnoses:        {len(diagnosis_df)}")
    print(f"Services:         {len(service_df)}")
    print(f"Dates:            {len(date_df)}")
    print(f"Claims:           {len(claim_df)}")
    print(f"Claim Lines:      {len(claim_line_df)}")
    print(f"Payments:         {len(payment_df)}")
    print(f"Authorizations:   {len(authorization_df)}")

    print()
    print("==========================================")
    print("AUTHORIZATION SAMPLE")
    print("==========================================")

    print(
        authorization_df.head(10)
    )
if __name__ == "__main__":
    main()