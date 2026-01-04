"""Database SQL queries and settings - Oracle."""

# SQL Queries - Oracle syntax (using :1, :2, etc. for parameters)
SQL_QUERIES = {
    'SELECT_REPORT': """
        SELECT report_id, alert_id 
        FROM IMP_REPORT_LOG
        WHERE report_id = :1
    """,
    'SELECT_REPORTS_BULK': """ 
        SELECT DISTINCT report_id, alert_id, SAR_folder_name
        FROM IMP_REPORT_LOG
        WHERE report_id IN ({placeholders})
    """,
    
    'UPDATE_REPORT_LOG': """
        UPDATE IMP_REPORT_LOG 
        SET report_date = :1, first_response_valid = :2, final_response_valid = :3, 
            received_date = :4, mispar_tkina = :5, status_desc = :6 
        WHERE report_id = :7
    """,
    
    'INSERT_STATUS_TRACKING': """
        INSERT INTO IMP_REPORT_STATUS_TRACKING 
        (Report_id, alert_id, update_date, status, comments, first_response_valid, final_response_valid)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': 1000,
    'TIMEOUT': 30
}

