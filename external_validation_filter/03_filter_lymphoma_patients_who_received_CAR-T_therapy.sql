/* Dialect: Google BigQuery Standard SQL
   Database: MIMIC-IV (v2.2) hosted on Google Cloud Platform
   Project: physionet-data (Public MIMIC-IV dataset)
*/

CREATE OR REPLACE TABLE
    Project_name.dataset_name.cart_lymphoma_patient_info AS
SELECT
    lymphoma.subject_id,
    lymphoma.hadm_id,
    cart.chartdate -- De-identificated
FROM
    (
    -- lymphoma patients
    SELECT DISTINCT subject_id, hadm_id
    FROM physionet-data.mimiciv_3_1_hosp.diagnoses_icd
    WHERE
        (icd_version = 10 AND (
            STARTS_WITH(icd_code, 'C82') OR
            STARTS_WITH(icd_code, 'C831') OR
            STARTS_WITH(icd_code, 'C833') OR
            STARTS_WITH(icd_code, 'C884')
        ))
        OR
        (icd_version = 9 AND (
            STARTS_WITH(icd_code, '2020') OR
            STARTS_WITH(icd_code, '2004') OR
            STARTS_WITH(icd_code, '2003') OR
            STARTS_WITH(icd_code, '2007')
        ))
) AS lymphoma
INNER JOIN (
    --CAR-T patients
    SELECT DISTINCT subject_id, hadm_id, chartdate
    FROM physionet-data.mimiciv_3_1_hosp.procedures_icd
    WHERE
        icd_version = 10
        AND icd_code IN (
            'XW033C3',
            'XW043C3',
            'XW033C7',
            'XW043C7',
            'XW033G7',
            'XW043G7'
        )
) AS cart
ON lymphoma.subject_id = cart.subject_id
   AND lymphoma.hadm_id = cart.hadm_id;  -- the same hospitalization
