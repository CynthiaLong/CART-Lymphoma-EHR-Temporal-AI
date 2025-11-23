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
-- 1. Retrieve discharge summaries
-- *******************************************************
SELECT
    t1.subject_id,
    t1.hadm_id,
    t1.car_t_procedure_date,
    t2.charttime AS note_time,
    'Discharge Summary' AS note_category,
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
    t2.charttime AS note_time,
    'Radiology Report' AS note_category,
    t2.text AS note_content
FROM
    CAR_T_PATIENTS AS t1
INNER JOIN
    physionet-data.mimiciv_note.radiology AS t2 
    ON t1.subject_id = t2.subject_id AND t1.hadm_id = t2.hadm_id
WHERE
    -- report date must be later than the CAR-T treatment date
    -- Since follow-up evaluations are typically not reported on the treatment day, use “>” to exclude reports generated before treatment.
    CAST(t2.charttime AS DATE) > t1.car_t_procedure_date
ORDER BY
subject_id, hadm_id, note_time;
