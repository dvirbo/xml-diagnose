import pyodbc
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from database.config import SQL_QUERIES, DB_SETTINGS, FIELD_MAPPINGS

@dataclass
class ReportUpdate:
    report_id: str
    alert_id: str
    status_divuah: str
    mispar_tkina: str
    received_date: str
    comments: str

class DatabaseUpdater:
    def __init__(self, connection: pyodbc.Connection):
        self.connection = connection
        self.cursor = connection.cursor()
        
    def _extract_report_data(self, report_data: Dict) -> Optional[ReportUpdate]:
        """Extract and validate report data."""
        try:
            first_response = report_data.get('FirstResponse', {})
            final_response = report_data.get('FinalResponse', {})
            
            return ReportUpdate(
                report_id=None,  # Will be set later
                alert_id=first_response.get(FIELD_MAPPINGS['ALERT_ID'], ''),
                status_divuah=final_response.get(FIELD_MAPPINGS['STATUS_DIVUAH'], ''),
                mispar_tkina=final_response.get(FIELD_MAPPINGS['MISPAR_TKINA'], ''),
                received_date=first_response.get(FIELD_MAPPINGS['RECEIVED_DATE'], ''),
                comments=final_response.get(FIELD_MAPPINGS['COMMENTS'], '')
            )
        except Exception as e:
            logging.error(f"Error extracting report data: {e}")
            return None
    
    def _get_existing_report_info(self, report_number: str) -> Tuple[Optional[str], Optional[str]]:
        """Get existing report and alert ID from database."""
        try:
            self.cursor.execute(SQL_QUERIES['SELECT_REPORT'], (report_number,))
            row = self.cursor.fetchone()
            return (row[0], row[1]) if row else (None, None)
        except Exception as e:
            logging.error(f"Error fetching report info for {report_number}: {e}")
            return (None, None)
    
    def _bulk_insert_report_logs(self, updates: List[ReportUpdate]) -> int:
        """Bulk insert report logs."""
        try:
            data = [
                (update.report_id, update.alert_id, update.status_divuah, 
                 update.comments, update.received_date, update.mispar_tkina, update.status_divuah)
                for update in updates
            ]
            
            self.cursor.executemany(SQL_QUERIES['INSERT_REPORT_LOG'], data)
            return len(data)
        except Exception as e:
            logging.error(f"Error in bulk insert report logs: {e}")
            raise
    
    def _bulk_update_status_tracking(self, updates: List[ReportUpdate]) -> int:
        """Bulk update status tracking."""
        try:
            data = [
                (update.received_date, DB_SETTINGS['DEFAULT_STATUS'],  #TODO: change the default status
                 update.status_divuah, update.report_id, update.alert_id)
                for update in updates
            ]
            
            self.cursor.executemany(SQL_QUERIES['UPDATE_STATUS_TRACKING'], data)
            return len(data)
        except Exception as e:
            logging.error(f"Error in bulk update status tracking: {e}")
            raise
    
    def update_database_bulk(self, reports: Dict) -> Dict:
        """
        Updates the database with the provided reports using bulk operations.
        
        Args:
            reports: Dictionary of report data
            
        Returns:
            Dict containing summary of updates and any errors
        """
        summary = {
            'successful_updates': [],
            'failed_updates': [],
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0
        }
        
        valid_updates = []
        
        try:
            # Process and validate all reports
            for report_number, report_data in reports.items():
                summary['total_processed'] += 1
                
                # Extract report data
                update_data = self._extract_report_data(report_data)
                if not update_data:
                    summary['failed_updates'].append({
                        'report_number': report_number,
                        'error': 'Failed to extract report data'
                    })
                    continue
                
                # Get existing report info
                report_id, alert_id = self._get_existing_report_info(report_number)
                
                if not alert_id:
                    summary['failed_updates'].append({
                        'report_number': report_number,
                        'error': f'Alert ID not found for report {report_number}'
                    })
                    continue
                
                # Set the report_id and validate alert_id
                update_data.report_id = report_id
                update_data.alert_id = alert_id
                
                valid_updates.append(update_data)
                summary['successful_updates'].append({
                    'report_number': report_number,
                    'report_id': report_id,
                    'alert_id': alert_id,
                    'status_divuah': update_data.status_divuah,
                    'mispar_tkina': update_data.mispar_tkina
                })
            
            # Perform bulk operations
            if valid_updates:
                # Process in batches
                batch_size = DB_SETTINGS['BATCH_SIZE']
                for i in range(0, len(valid_updates), batch_size):
                    batch = valid_updates[i:i + batch_size]
                    
                    # Bulk insert report logs
                    self._bulk_insert_report_logs(batch)
                    
                    # Bulk update status tracking
                    self._bulk_update_status_tracking(batch)
                    
                    # Commit batch
                    self.connection.commit()
                    
                    logging.info(f"Processed batch {i//batch_size + 1}: {len(batch)} records")
            
            summary['total_successful'] = len(valid_updates)
            summary['total_failed'] = summary['total_processed'] - summary['total_successful']
            
            logging.info(f"Database update completed: {summary['total_successful']}/{summary['total_processed']} successful")
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error in bulk database update: {e}")
            summary['failed_updates'].append({
                'error': f'Bulk operation failed: {e}'
            })
        
        return summary['successful_updates']

def update_db(connection: pyodbc.Connection, reports: Dict) -> str:
    """
    Updates the database with the provided reports using bulk operations.
    
    Args:
        connection: Database connection
        reports: Dictionary of report data
        
    Returns:
        str: Summary of the updates made
    """
    updater = DatabaseUpdater(connection)
    summary = updater.update_database_bulk(reports)
    
    return summary