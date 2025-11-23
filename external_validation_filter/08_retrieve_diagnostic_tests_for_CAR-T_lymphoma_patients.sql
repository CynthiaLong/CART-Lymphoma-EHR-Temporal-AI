/* Dialect: Google BigQuery Standard SQL
   Database: MIMIC-IV (v2.2) hosted on Google Cloud Platform
   Project: physionet-data (Public MIMIC-IV dataset)
*/

WITH CAR_T_PATIENTS AS (
    -- patient info table
    SELECT
        subject_id,
        hadm_id,
        chartdate as car_t_procedure_date
    FROM
        ` Project_name.dataset_name.cart_lymphoma_patient_info`
)
SELECT DISTINCT
    d.itemid,
    d.label,      -- name of the test (e.g., 'LDH', 'WBC Count')
    d.category,   -- test category (e.g., 'Blood Gas', 'Chemistry')
    d.fluid       -- specimen type (e.g., 'Blood', 'Urine')
FROM
    `physionet-data.mimiciv_3_1_hosp.labevents` AS le
JOIN
    CAR_T_PATIENTS AS p
    ON le.subject_id = p.subject_id AND le.hadm_id = p.hadm_id
JOIN
    `physionet-data.mimiciv_3_1_hosp.d_labitems` AS d
    ON le.itemid = d.itemid
WHERE
    -- Ensure that at least one value is not null.
    (le.valuenum IS NOT NULL OR le.value IS NOT NULL)
ORDER BY
d.category, d.label;
