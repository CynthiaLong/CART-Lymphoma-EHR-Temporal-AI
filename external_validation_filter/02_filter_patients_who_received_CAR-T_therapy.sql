/* Dialect: Google BigQuery Standard SQL
   Database: MIMIC-IV (v2.2) hosted on Google Cloud Platform
   Project: physionet-data (Public MIMIC-IV dataset)
*/

-- Find out all the ICD codes of CAR—T therapy both currently used and aborted 
SELECT 
    icd_code,
    long_title,
    icd_version
FROM 
    physionet-data.mimiciv_3_1_hosp.d_icd_procedures
WHERE 
    LOWER(long_title) LIKE '%chimeric antigen receptor%';




SELECT
  COUNT(DISTINCT subject_id) AS total_patients
FROM
  physionet-data.mimiciv_3_1_hosp.procedures_icd
WHERE
  icd_version = 10
  AND icd_code IN (
    'XW033C3', -- (Aborted, could appear in the data) 
    'XW043C3', -- (Aborted, could appear in the data)
    'XW033C7', -- (Autologous CAR-T, Peripheral Vein)
    'XW043C7', -- (Autologous CAR-T, Central Vein) 有3个...
    'XW033G7', -- (Allogeneic CAR-T, Peripheral Vein)
    'XW043G7'  -- (Allogeneic CAR-T, Central Vein)
  )