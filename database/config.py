# Database configuration
DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'ifs-lab-2025',
    'DATABASE': 'actone',
    'USERNAME': 'sa',
    'PASSWORD': ''
}

# Connection string template
CONNECTION_STRING_TEMPLATE = (
    "DRIVER={DRIVER};"
    "SERVER={SERVER};"
    "DATABASE={DATABASE};"
    "UID={USERNAME};"
    "PWD={PASSWORD};"
)
# SQL Queries
SQL_QUERIES = {
    'SELECT_REPORT': """
        SELECT report_id, alert_id 
        FROM [IMP_REPORT_LOG]
        WHERE report_id = ?
    """,
    #UPDATE
    'SELECT_REPORTS_BULK': """ 
    SELECT report_id, alert_id, SAR_folder_name
    FROM [IMP_REPORT_LOG]
    WHERE report_id IN ({placeholders})
    """,
    
    'UPDATE_REPORT_LOG': """
        UPDATE INTO IMP_REPORT_LOG 
        (report_id, alert_id, comments, received_date, mispar_tkina, status_divuah) 
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    
    'INSERT_STATUS_TRACKING': """
        INSERT IMP_REPORT_STATUS_TRACKING 
        SET Update_date = ?, Status = ?, Comments = ? 
        WHERE Report_id = ? AND alert_id = ?
    """,
    
    
    'UPDATE_ALERTS': """
        UPDATE alerts 
        SET p17 = ?, p18 = ? 
        WHERE alert_id = ?
    """
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': 1000,
    'TIMEOUT': 30
}

