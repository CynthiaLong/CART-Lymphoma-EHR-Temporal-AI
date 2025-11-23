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
        Project_name.dataset_name.cart_lymphoma_patient_info
)
-- *******************************************************
-- 1. Retrieve Discharge Summaries
-- *******************************************************
SELECT
    t1.subject_id,
    t1.hadm_id,
    t1.car_t_procedure_date,
    t2.charttime AS note_time,
    'Discharge Summary' AS note_category,
    t2.note_type,
    t2.note_seq,
    t2.text AS note_content
FROM
    CAR_T_PATIENTS AS t1
INNER JOIN
    physionet-data.mimiciv_note.discharge AS t2
    ON t1.subject_id = t2.subject_id AND t1.hadm_id = t2.hadm_id

UNION ALL

-- *******************************************************
-- 2. Retrieve Radiology Reports
-- *******************************************************
SELECT
    t1.subject_id,
    t1.hadm_id,
    t1.car_t_procedure_date,
    t3.charttime AS note_time,
    'Radiology Report' AS note_category,
    t3.note_type,
    t3.note_seq,
    t3.text AS note_content
FROM
    CAR_T_PATIENTS AS t1
INNER JOIN
    physionet-data.mimiciv_note.radiology AS t3
    ON t1.subject_id = t3.subject_id AND t1.hadm_id = t3.hadm_id
-- To identify prior treatment information, reports from both pre- and post-CAR-T infusion were reviewed.
    -- CAST(t2.charttime AS DATE) > t1.car_t_procedure_date
-- ORDER BY
--     subject_id, hadm_id, note_time;
