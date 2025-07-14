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
    
    'INSERT_REPORT_LOG': """
        INSERT INTO IMP_REPORT_LOG 
        (report_id, alert_id, status, comments, received_date, mispar_tkina, status_divuah) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    
    'UPDATE_STATUS_TRACKING': """
        UPDATE IMP_REPORT_STATUS_TRACKING 
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
    'DEFAULT_STATUS': 'valid',
    'TIMEOUT': 30
}

# Field mappings
FIELD_MAPPINGS = {
    'STATUS_DIVUAH': 'ReportInstanceLegalStatusDesc',
    'MISPAR_TKINA': 'ReportInstanceReference',
    'COMMENTS': 'ReportInstanceStatusReason',
    'RECEIVED_DATE': 'ReportDate',
    'ALERT_ID': 'ReportInstanceReference'
}