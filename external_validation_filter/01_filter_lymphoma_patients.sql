/* Dialect: Google BigQuery Standard SQL
   Database: MIMIC-IV (v2.2) hosted on Google Cloud Platform
   Project: physionet-data (Public MIMIC-IV dataset)
*/

SELECT
  COUNT(DISTINCT subject_id) AS total_patients  -- 1074 non hodgkin lymphoma patients
FROM
  physionet-data.mimiciv_3_1_hosp.diagnoses_icd
WHERE
-- the ICD 10 code of the specific type of lymphoma is obtained from icd10cm-Code Descriptions-2026.zip, which can be downloaded from CDC official website https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2026/
  (icd_version = 10
    AND (STARTS_WITH(icd_code, 'C82')
      OR STARTS_WITH(icd_code, 'C831')
      OR STARTS_WITH(icd_code, 'C833')
      OR STARTS_WITH(icd_code, 'C884'))
  )
  OR
-- the ICD 9 code of the specific type of lymphoma is obtained from Dtab12.zip, which can be downloaded from CDC official website https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD9-CM/2011/
  (icd_version = 9
    AND (STARTS_WITH(icd_code, '2020')
      OR STARTS_WITH(icd_code, '2004')
      OR STARTS_WITH(icd_code, '2003')
      OR STARTS_WITH(icd_code, '2007'))
  )
