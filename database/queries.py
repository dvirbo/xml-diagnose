"""Database SQL queries and settings."""

# SQL Queries
SQL_QUERIES = {
    'SELECT_REPORT': """
        SELECT report_id, alert_id 
        FROM [IMP_REPORT_LOG]
        WHERE report_id = ?
    """,
    'SELECT_REPORTS_BULK': """ 
    SELECT distinct report_id, alert_id, SAR_folder_name
    FROM [IMP_REPORT_LOG]
    WHERE report_id IN ({placeholders})
    """,
    
    'UPDATE_REPORT_LOG': """
        UPDATE IMP_REPORT_LOG 
        SET report_date = ?, first_response_valid = ?, final_response_valid = ?, received_date = ?, mispar_tkina = ?, status_desc = ? 
        WHERE report_id = ?
    """,
    
    'INSERT_STATUS_TRACKING': """
        INSERT INTO IMP_REPORT_STATUS_TRACKING 
        (Report_id, alert_id, update_date, status, comments, first_response_valid, final_response_valid)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': 1000,
    'TIMEOUT': 30
}

