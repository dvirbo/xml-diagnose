import pyodbc
import logging


server = 'IFS-LAB-2025'  
database = 'master'  
username = 'sa'  
password = 'Mat1234!'  

def establish_sql_connection():
    """
    Establishes a connection to a SQL Server database using the provided connection parameters.
    Returns:
        connection (pyodbc.Connection or None): A connection object if successful, otherwise None.
    Logs:
        - Info message on successful connection.
        - Error message if connection fails.
    Raises:
        Does not raise exceptions; logs errors and returns None on failure.
    Note:
        The variables 'server', 'database', 'username', and 'password' must be defined in the scope where this function is called.
    """

    try:
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        connection = pyodbc.connect(connection_string)
        logging.info("Connection to SQL Server established successfully.")
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to SQL Server: {e}")
        return None


def update_db(connection, reports):
    """
    Updates the database with the provided reports.
    Returns:
        summary (str): A short text summary of the updates made.
    """
    cursor = connection.cursor()
    summary_lines = []
    try:
        for report_number, report_data in reports.items():
            alert_id = report_data['FirstResponse']['ReportInstanceReference']
            cursor.execute(
                "SELECT report_id, alert_id FROM IMP_REPORT_LOG WHERE report_id = ?", (report_number,)
            )
            row = cursor.fetchone()
            report_id = row[0] if row else None
            alert_id = row[1] if row else None

            if alert_id:
                status_divuah = report_data["FinalResponse"].get("ReportInstanceLegalStatusDesc", "")
                mispar_tkina = report_data["FinalResponse"].get("ReportInstanceReference", "")
                received_date = report_data['FirstResponse']['ReportDate']
                comments = report_data["FinalResponse"].get("ReportInstanceStatusReason", "")
                '''
                # Option to update the alert directly from the DB
                cursor.execute(
                    "update alerts set p17 = ? ,  p18 = ? where alert_id = ?",
                    (status_divuah, mispar_tkina, alert_id),
                )
                connection.commit()                
                '''
                # Insert or update the IMP_REPORT_LOG table
                cursor.execute(
                    "INSERT INTO IMP_REPORT_LOG (report_id, alert_id, status, comments, received_date, mispar_tkina, status_divuah) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (report_id, alert_id, status_divuah, comments, received_date, mispar_tkina, status_divuah)
                )
                connection.commit()
                
                # Update the IMP_REPORT_STATUS_TRACKING table
                cursor.execute(
                    "UPDATE IMP_REPORT_STATUS_TRACKING SET Update_date = ?, Status = ?, Comments= ? where Report_id = ? and alert_id = ?",
                    (received_date, 'valid', status_divuah, report_id, alert_id)
                )
                connection.commit()

                summary_lines.append({
                    "report_id": report_id,
                    "alert_id": alert_id,
                    "status_divuah": status_divuah,
                    "mispar_tkina": mispar_tkina
                })
            else:
                logging.error(f"Alert ID {alert_id} not found for report {report_number}.")

    except Exception as e:
        logging.error(f"Error updating database: {e}")
        summary_lines.append(f"Error updating database: {e}")

    return "\n".join(summary_lines)
