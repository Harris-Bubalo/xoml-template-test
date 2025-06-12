WITH
    jobs_info AS (
        -- Information about the parts in the job.
        -- At the JOB level.
        SELECT
            _id AS job_id,
            -- Since jobs can only have a single line item, no jobs will have
            -- multiple process groups.
            ANY_VALUE(process_group) AS process_group,
            MIN(opf.process_simple_lathe) AS is_lathe,
            MAX(opf.process_3_axis_mill) AS is_3_axis,
            MAX(opf.machining_center_space_bbox_x_max) AS machining_center_space_bbox_x_max,
            MAX(opf.machining_center_space_bbox_y_max) AS machining_center_space_bbox_y_max,
            MAX(opf.machining_center_space_bbox_z_max) AS machining_center_space_bbox_z_max,
            MAX(opf.lathe_length) AS lathe_length,
            MAX(opf.lathe_radius) AS lathe_radius
        FROM xometry_models.jobs.jobs_orders_outsourced_part_details AS joopd
            -- Inner join since the geometry parts are key for the analysis.
            INNER JOIN feature_store_db.feature_store.ordered_part_features AS opf ON (
                joopd.ordered_part_id = opf.ordered_part_id
            )
        GROUP BY
            joopd._id
        HAVING
            COUNT(DISTINCT part_id) = 1
    ),
    offers_status AS (
        -- Offer status: either accepted, rejected due to outside of capabilities or 'Other'.
        -- At the OFFER level.
        SELECT
            jo._id AS job_id,
            jo.unique_id AS offer_id,
            jo.job_offer_start_time,
            jo.partner_id,
            CASE
                WHEN jo.accepted_offer_flag = 1 THEN 'Accepted'
                WHEN jorr.reason = 'outside_of_capabilities' THEN 'Rejected'
                ELSE 'Other'
            END AS status
        FROM
            xometry_models.jobs.jobs_offers AS jo
        LEFT JOIN xometry_models.jobs.jobs_offers_rejection_reasons AS jorr USING(_id, _id_1)
    )

SELECT
    os.job_id,
    os.offer_id,
    os.partner_id,
    ji.is_lathe,
    ji.is_3_axis,
    ji.machining_center_space_bbox_x_max,
    ji.machining_center_space_bbox_y_max,
    ji.machining_center_space_bbox_z_max,
    ji.lathe_length,
    ji.lathe_radius,
    CASE
        WHEN os.status = 'Accepted' THEN 1
        WHEN os.status = 'Rejected' THEN 0
        ELSE NULL
    END AS accepted_or_rejected
FROM
    offers_status AS os
    -- Inner join since the geometry parts are key for the analysis.
    INNER JOIN jobs_info AS ji USING(job_id)
WHERE
    os.job_offer_start_time >= '2025-01-01'
    AND os.job_offer_start_time < '2025-02-01'
    AND ji.process_group = 'CNC'
    AND accepted_or_rejected IS NOT NULL
 ORDER BY
    os.job_offer_start_time ASC