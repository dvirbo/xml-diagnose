"""Export processed reports to CSV."""
import csv
import logging
import os
from datetime import datetime
from typing import List, Dict


# Fixed Hebrew column headers (order matches export row keys)
CSV_HEADERS = [
    'סטטוס תגובה',    # response_status
    'קוד שגיאה',       # error_code
    'תיאור שגיאה',     # error_description
    'שם תיקיית דיווח', # report_folder
    'מספר דיווח',      # report_id
    'מספר התראה'       # alert_id
]

# Ordered keys for export row (must match CSV_HEADERS)
EXPORT_ROW_KEYS = [
    'response_status',
    'error_code',
    'error_description',
    'report_folder',
    'report_id',
    'alert_id'
]


def export_reports_to_csv(export_rows: List[Dict], export_dir: str) -> str:
    """
    Export report rows to a CSV file with Hebrew headers.
    
    Args:
        export_rows: List of dicts with keys: response_status, error_code,
                     error_description, report_folder, report_id, alert_id
        export_dir: Directory path for output CSV (created if not exists)
    
    Returns:
        Full path of the created CSV file, or empty string if no rows
    """
    if not export_rows:
        logging.info("No export rows to write, skipping CSV export")
        return ''
    
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = 'reports_{}.csv'.format(timestamp)
    filepath = os.path.join(export_dir, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            for row in export_rows:
                writer.writerow([row.get(k, '') for k in EXPORT_ROW_KEYS])
        
        logging.info("Exported {} reports to {}".format(len(export_rows), filepath))
        return filepath
        
    except Exception as e:
        logging.error("Failed to export CSV: {}".format(e))
        raise
