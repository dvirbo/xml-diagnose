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
    """
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': 1000,
    'TIMEOUT': 30
}

