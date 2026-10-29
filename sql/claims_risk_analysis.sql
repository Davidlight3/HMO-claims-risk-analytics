
USE [HMO_Claims_Risk_Analytics];
GO

/* =========================================================
   HMO Claims Risk & Financial Leakage Analytics
   Script: Claims Risk and Financial Exposure Analysis
   Purpose: Investigate claims risk, HMO performance,
            provider risk, and payment discrepancies.

   Important:
   Risk flags identify claims for further review.
   They do not establish confirmed fraud or actual loss.
   ========================================================= */

-- 1. Claims by risk category
SELECT
    Risk_Level,
    COUNT_BIG(*) AS Claim_Count,
    SUM(Claim_Amount) AS Total_Claim_Amount,
    AVG(CAST(Claim_Amount AS DECIMAL(18,2))) AS Average_Claim_Amount
FROM rpt.vw_Claim_Risk
GROUP BY Risk_Level
ORDER BY
    CASE Risk_Level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;
GO

-- 2. Highest-risk claims for investigation
SELECT TOP (50)
    *
FROM rpt.vw_High_Risk_Claims
ORDER BY Risk_Score DESC;
GO

-- 3. Compare risk across HMOs
SELECT *
FROM rpt.vw_HMO_Risk;
GO

-- 4. Review payment discrepancies
SELECT *
FROM rpt.vw_Payment_Leakage;
GO

-- 5. Review providers with risk indicators
SELECT *
FROM rpt.vw_Provider_Risk;
GO

-- 6. Review unusual service costs
SELECT *
FROM rpt.vw_Service_Cost_Anomalies;
GO
