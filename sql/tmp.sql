select xml_log.report_id, xml_log.alert_id
FROM imp_report_xml_log xml_log
JOIN imp_report_log log
    ON xml_log.report_id = log.report_id
   AND xml_log.alert_id  = log.alert_id
WHERE (xml_log.report_id, xml_log.alert_id) IN (
    SELECT report_id, alert_id
    FROM imp_report_processes_log
    WHERE process_id = (
        SELECT process_id
        FROM (
            SELECT process_id
            FROM imp_report_processes_log
            ORDER BY start_time DESC
        )
        WHERE ROWNUM = 1
    )
);