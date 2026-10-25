USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_Claim_Risk]    Script Date: 10/25/2026 8:40:31 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [rpt].[vw_Claim_Risk]
AS
SELECT
    r.Claim_ID,
    r.Claim_Date,

    r.Member_ID,
    CONCAT(m.First_Name, ' ', m.Last_Name) AS Member_Name,
    m.Gender,
    m.Age_Group,
    m.State AS Member_State,

    r.Provider_ID,
    p.Provider_Name,
    p.Provider_Type,
    p.Provider_Tier,
    p.State AS Provider_State,

    h.HMO_ID,
    h.HMO_Name,

    r.Plan_ID,
    pl.Plan_Name,
    pl.Plan_Type,

    c.Diagnosis_ID,
    d.Diagnosis_Code,
    d.Diagnosis_Name,
    d.Diagnosis_Category,

    c.Claim_Type,
    c.Claim_Status,

    r.Claim_Amount,
    r.Approved_Amount,
    r.Rejected_Amount,

    r.Risk_Score,
    r.Risk_Level,

    r.Anomaly_Record_Count,
    r.Distinct_Anomaly_Type_Count,

    r.High_Value_Flag,
    r.Duplicate_Flag,
    r.Frequency_Flag,
    r.Suspicious_Timing_Flag,
    r.Provider_Risk_Flag,
    r.Service_Cost_Anomaly_Flag,
    r.Excessive_Quantity_Flag,
    r.Missing_Authorization_Flag,
    r.Plan_Coverage_Flag,

    r.Risk_Drivers

FROM dw.Fact_Claim_Risk r

INNER JOIN dw.Fact_Claims c
    ON r.Claim_ID = c.Claim_ID

LEFT JOIN dw.Dim_Member m
    ON r.Member_ID = m.Member_ID

LEFT JOIN dw.Dim_Provider p
    ON r.Provider_ID = p.Provider_ID

LEFT JOIN dw.Dim_HMO h
    ON c.HMO_ID = h.HMO_ID

LEFT JOIN dw.Dim_Plan pl
    ON r.Plan_ID = pl.Plan_ID

LEFT JOIN dw.Dim_Diagnosis d
    ON c.Diagnosis_ID = d.Diagnosis_ID;
GO




USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_High_Risk_Claims]    Script Date: 10/25/2026 8:42:42 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [rpt].[vw_High_Risk_Claims]
AS
SELECT
    Claim_ID,
    Claim_Date,
    Member_ID,
    Member_Name,
    Provider_ID,
    Provider_Name,
    Provider_Type,
    Provider_Tier,
    HMO_ID,
    HMO_Name,
    Plan_ID,
    Plan_Name,
    Diagnosis_Name,
    Diagnosis_Category,
    Claim_Type,
    Claim_Status,
    Claim_Amount,
    Approved_Amount,
    Rejected_Amount,
    Risk_Score,
    Risk_Level,
    Anomaly_Record_Count,
    Distinct_Anomaly_Type_Count,
    High_Value_Flag,
    Duplicate_Flag,
    Frequency_Flag,
    Suspicious_Timing_Flag,
    Provider_Risk_Flag,
    Service_Cost_Anomaly_Flag,
    Excessive_Quantity_Flag,
    Missing_Authorization_Flag,
    Plan_Coverage_Flag,
    Risk_Drivers
FROM rpt.vw_Claim_Risk
WHERE Risk_Level IN ('High', 'Critical');
GO



USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_HMO_Risk]    Script Date: 10/25/2026 8:43:23 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [rpt].[vw_HMO_Risk]
AS
SELECT
    c.HMO_ID,
    h.HMO_Name,

    COUNT(DISTINCT c.Claim_ID) AS Total_Claims,

    COUNT(DISTINCT c.Member_ID) AS Members_With_Claims,

    COUNT(DISTINCT c.Provider_ID) AS Active_Providers,

    SUM(c.Claim_Amount) AS Total_Claim_Amount,

    SUM(c.Approved_Amount) AS Total_Approved_Amount,

    SUM(c.Rejected_Amount) AS Total_Rejected_Amount,

    AVG(c.Claim_Amount) AS Average_Claim_Amount,

    SUM(
        CASE
            WHEN r.Risk_Level IN ('High', 'Critical')
            THEN 1
            ELSE 0
        END
    ) AS High_Risk_Claims,

    SUM(
        CASE
            WHEN r.Duplicate_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Duplicate_Flag_Count,

    SUM(
        CASE
            WHEN r.Missing_Authorization_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Missing_Authorization_Count,

    SUM(
        CASE
            WHEN r.Provider_Risk_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Provider_Risk_Count,

    SUM(
        CASE
            WHEN r.Plan_Coverage_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Plan_Coverage_Issue_Count,

    MAX(r.Risk_Score) AS Maximum_Risk_Score

FROM dw.Fact_Claims c

INNER JOIN dw.Fact_Claim_Risk r
    ON c.Claim_ID = r.Claim_ID

LEFT JOIN dw.Dim_HMO h
    ON c.HMO_ID = h.HMO_ID

GROUP BY
    c.HMO_ID,
    h.HMO_Name;
GO




USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_Member_Utilization]    Script Date: 10/25/2026 8:44:09 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [rpt].[vw_Member_Utilization]
AS
SELECT
    c.Member_ID,

    CONCAT(m.First_Name, ' ', m.Last_Name) AS Member_Name,

    m.Gender,
    m.Age_Group,
    m.State,
    m.City,

    m.HMO_ID,
    h.HMO_Name,

    m.Plan_ID,
    pl.Plan_Name,
    pl.Plan_Type,

    COUNT(DISTINCT c.Claim_ID) AS Total_Claims,

    SUM(c.Claim_Amount) AS Total_Claim_Amount,

    SUM(c.Approved_Amount) AS Total_Approved_Amount,

    SUM(c.Rejected_Amount) AS Total_Rejected_Amount,

    AVG(c.Claim_Amount) AS Average_Claim_Amount,

    SUM(
        CASE
            WHEN r.Frequency_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Frequency_Flag_Count,

    SUM(
        CASE
            WHEN r.High_Value_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS High_Value_Claim_Count,

    SUM(
        CASE
            WHEN r.Risk_Level IN ('High', 'Critical')
            THEN 1
            ELSE 0
        END
    ) AS High_Risk_Claim_Count,

    MAX(r.Risk_Score) AS Maximum_Risk_Score

FROM dw.Fact_Claims c

INNER JOIN dw.Fact_Claim_Risk r
    ON c.Claim_ID = r.Claim_ID

LEFT JOIN dw.Dim_Member m
    ON c.Member_ID = m.Member_ID

LEFT JOIN dw.Dim_HMO h
    ON c.HMO_ID = h.HMO_ID

LEFT JOIN dw.Dim_Plan pl
    ON c.Plan_ID = pl.Plan_ID

GROUP BY
    c.Member_ID,
    m.First_Name,
    m.Last_Name,
    m.Gender,
    m.Age_Group,
    m.State,
    m.City,
    m.HMO_ID,
    h.HMO_Name,
    m.Plan_ID,
    pl.Plan_Name,
    pl.Plan_Type;
GO




USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_Payment_Leakage]    Script Date: 10/25/2026 8:44:57 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [rpt].[vw_Payment_Leakage]
AS
SELECT
    c.Claim_ID,
    c.Claim_Date,

    c.Member_ID,

    c.Provider_ID,
    p.Provider_Name,

    c.HMO_ID,
    h.HMO_Name,

    c.Plan_ID,
    pl.Plan_Name,

    c.Claim_Amount,
    c.Approved_Amount,
    c.Rejected_Amount,

    ISNULL(SUM(pay.Payment_Amount), 0) AS Total_Paid_Amount,

    c.Approved_Amount
        - ISNULL(SUM(pay.Payment_Amount), 0)
        AS Approved_Unpaid_Amount,

    c.Claim_Amount
        - c.Approved_Amount
        AS Rejected_or_Unapproved_Amount,

    COUNT(pay.Payment_ID) AS Payment_Count,

    MAX(pay.Payment_Date) AS Last_Payment_Date

FROM dw.Fact_Claims c

LEFT JOIN dw.Fact_Payments pay
    ON c.Claim_ID = pay.Claim_ID

LEFT JOIN dw.Dim_Provider p
    ON c.Provider_ID = p.Provider_ID

LEFT JOIN dw.Dim_HMO h
    ON c.HMO_ID = h.HMO_ID

LEFT JOIN dw.Dim_Plan pl
    ON c.Plan_ID = pl.Plan_ID

GROUP BY
    c.Claim_ID,
    c.Claim_Date,
    c.Member_ID,
    c.Provider_ID,
    p.Provider_Name,
    c.HMO_ID,
    h.HMO_Name,
    c.Plan_ID,
    pl.Plan_Name,
    c.Claim_Amount,
    c.Approved_Amount,
    c.Rejected_Amount;
GO




USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_Provider_Risk]    Script Date: 10/25/2026 8:45:38 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [rpt].[vw_Provider_Risk]
AS
SELECT
    c.Provider_ID,
    p.Provider_Name,
    p.Provider_Type,
    p.Provider_Tier,
    p.State,
    p.City,
    p.Accreditation_Status,

    COUNT(DISTINCT c.Claim_ID) AS Total_Claims,

    SUM(c.Claim_Amount) AS Total_Claim_Amount,

    SUM(c.Approved_Amount) AS Total_Approved_Amount,

    SUM(c.Rejected_Amount) AS Total_Rejected_Amount,

    AVG(c.Claim_Amount) AS Average_Claim_Amount,

    COUNT(
        CASE
            WHEN r.Risk_Level IN ('High', 'Critical')
            THEN 1
        END
    ) AS High_Risk_Claims,

    SUM(
        CASE
            WHEN r.Provider_Risk_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Provider_Risk_Flag_Count,

    SUM(
        CASE
            WHEN r.Duplicate_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Duplicate_Flag_Count,

    SUM(
        CASE
            WHEN r.Missing_Authorization_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Missing_Authorization_Count,

    SUM(
        CASE
            WHEN r.Plan_Coverage_Flag = 1
            THEN 1
            ELSE 0
        END
    ) AS Plan_Coverage_Flag_Count,

    MAX(r.Risk_Score) AS Maximum_Risk_Score

FROM dw.Fact_Claims c

INNER JOIN dw.Fact_Claim_Risk r
    ON c.Claim_ID = r.Claim_ID

LEFT JOIN dw.Dim_Provider p
    ON c.Provider_ID = p.Provider_ID

GROUP BY
    c.Provider_ID,
    p.Provider_Name,
    p.Provider_Type,
    p.Provider_Tier,
    p.State,
    p.City,
    p.Accreditation_Status;
GO




USE [HMO_Claims_Risk_Analytics]
GO

/****** Object:  View [rpt].[vw_Service_Cost_Anomalies]    Script Date: 10/25/2026 8:46:25 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [rpt].[vw_Service_Cost_Anomalies]
AS
SELECT
    cl.Claim_Line_ID,
    cl.Claim_ID,

    c.Claim_Date,

    c.Member_ID,

    c.Provider_ID,
    p.Provider_Name,

    c.HMO_ID,
    h.HMO_Name,

    c.Plan_ID,
    pl.Plan_Name,

    cl.Service_ID,
    s.Service_Name,
    s.Service_Category,
    s.Inpatient_Outpatient,

    cl.Quantity,
    cl.Unit_Cost,
    cl.Line_Amount,
    cl.Approved_Line_Amount,
    cl.Rejected_Line_Amount,

    cl.Authorization_Required,
    cl.Authorization_Status,

    r.Service_Cost_Anomaly_Flag,
    r.Excessive_Quantity_Flag,
    r.Risk_Level,
    r.Risk_Score

FROM dw.Fact_Claim_Lines cl

INNER JOIN dw.Fact_Claims c
    ON cl.Claim_ID = c.Claim_ID

INNER JOIN dw.Fact_Claim_Risk r
    ON cl.Claim_ID = r.Claim_ID

LEFT JOIN dw.Dim_Service s
    ON cl.Service_ID = s.Service_ID

LEFT JOIN dw.Dim_Provider p
    ON c.Provider_ID = p.Provider_ID

LEFT JOIN dw.Dim_HMO h
    ON c.HMO_ID = h.HMO_ID

LEFT JOIN dw.Dim_Plan pl
    ON c.Plan_ID = pl.Plan_ID

WHERE
    r.Service_Cost_Anomaly_Flag = 1
    OR r.Excessive_Quantity_Flag = 1;
GO


