
USE [HMO_Claims_Risk_Analytics];
GO

/* =========================================================
   HMO Claims Risk Analytics
   Warehouse Data Quality Checks
   Purpose: Validate key table counts and dimension keys
   ========================================================= */

-- 1. Warehouse row counts
SELECT 'dw.Dim_HMO' AS TableName, COUNT_BIG(*) AS TotalRows
FROM dw.Dim_HMO
UNION ALL
SELECT 'dw.Dim_Plan', COUNT_BIG(*) FROM dw.Dim_Plan
UNION ALL
SELECT 'dw.Dim_Member', COUNT_BIG(*) FROM dw.Dim_Member
UNION ALL
SELECT 'dw.Dim_Provider', COUNT_BIG(*) FROM dw.Dim_Provider
UNION ALL
SELECT 'dw.Dim_Diagnosis', COUNT_BIG(*) FROM dw.Dim_Diagnosis
UNION ALL
SELECT 'dw.Dim_Service', COUNT_BIG(*) FROM dw.Dim_Service
UNION ALL
SELECT 'dw.Dim_Date', COUNT_BIG(*) FROM dw.Dim_Date
UNION ALL
SELECT 'dw.Fact_Claims', COUNT_BIG(*) FROM dw.Fact_Claims
UNION ALL
SELECT 'dw.Fact_Claim_Lines', COUNT_BIG(*) FROM dw.Fact_Claim_Lines
UNION ALL
SELECT 'dw.Fact_Payments', COUNT_BIG(*) FROM dw.Fact_Payments
UNION ALL
SELECT 'dw.Fact_Authorizations', COUNT_BIG(*) FROM dw.Fact_Authorizations
UNION ALL
SELECT 'dw.Fact_Claim_Risk', COUNT_BIG(*) FROM dw.Fact_Claim_Risk;
GO

-- 2. Duplicate HMO business keys
SELECT HMO_ID, COUNT_BIG(*) AS DuplicateCount
FROM dw.Dim_HMO
GROUP BY HMO_ID
HAVING COUNT_BIG(*) > 1;
GO

-- 3. Duplicate plan business keys
SELECT Plan_ID, COUNT_BIG(*) AS DuplicateCount
FROM dw.Dim_Plan
GROUP BY Plan_ID
HAVING COUNT_BIG(*) > 1;
GO

-- 4. Duplicate member business keys
SELECT Member_ID, COUNT_BIG(*) AS DuplicateCount
FROM dw.Dim_Member
GROUP BY Member_ID
HAVING COUNT_BIG(*) > 1;
GO
