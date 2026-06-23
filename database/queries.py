"""Database SQL queries and settings - Oracle."""

# SQL Queries - Oracle syntax (using :1, :2, etc. for parameters)
SQL_QUERIES = {
    'SELECT_REPORT': """
        SELECT REPORT_ID, ALERT_ID 
        FROM IMP_REPORT_LOG
        WHERE REPORT_ID = :1
    """,
    'SELECT_REPORTS_BULK': """ 
        SELECT DISTINCT REPORT_ID, ALERT_ID, SAR_FOLDER_NAME
        FROM IMP_REPORT_LOG
        WHERE REPORT_ID IN ({placeholders})
    """,
    
    'UPDATE_REPORT_LOG': """
        UPDATE IMP_REPORT_LOG 
        SET FIRST_RESPONSE_ORIG = :1, FINAL_RESPONSE_VALID = :2, 
            RECEIVED_DATE = :3, MISPAR_TKINA = :4, STATUS_DESC = :5 
        WHERE REPORT_ID = :6
    """,
    
    'INSERT_STATUS_TRACKING': """
        INSERT INTO IMP_REPORT_STATUS_TRACKING 
        (REPORT_ID, ALERT_ID, UPDATE_DATE, TECH_COMMENT, BUSINESS_COMMENT)
        VALUES (:1, :2, :3, :4, :5)
    """,
    
    'UPDATE_ALERT': """
        UPDATE actone.alerts 
        SET p17 = :1, p19 = :2 
        WHERE alert_id = :3
    """,
    
    'GET_REPORTS_FROM_LATEST_PROCESS': """
        SELECT DISTINCT xml_log.report_id
        FROM imp_report_xml_log xml_log
        JOIN imp_report_log log
            ON xml_log.report_id = log.report_id
           AND xml_log.alert_id = log.alert_id
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
        )
    """,
    
    'GET_REPORT_NUMBERS_BY_IDS': """
        SELECT DISTINCT REPORT_ID, ALERT_ID
        FROM IMP_REPORT_LOG
        WHERE REPORT_ID IN ({placeholders})
    """,

    'GET_REPORTS_NO_RESPONSE': """
        SELECT DISTINCT REPORT_ID, ALERT_ID, SAR_FOLDER_NAME
        FROM IMP_REPORT_LOG
        WHERE FIRST_RESPONSE_ORIG IS NULL
          AND FINAL_RESPONSE_VALID IS NULL
    """
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': 1000,
    'TIMEOUT': 30
}

