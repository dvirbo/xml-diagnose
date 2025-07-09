import os
import logging
from db_usage import update_db
from establish_db import connect_to_database
from report_xml_classifier_v2 import classify_reports_by_status, export_reports_to_csv, parse_xml_files
from update_alert_rest import process_alert
from login_and_get_session import login_and_get_session

logging.basicConfig(level=logging.INFO)

def main(directory: str) -> None:

    first_responses, final_responses = parse_xml_files(directory)
    error_reports, valid_reports = classify_reports_by_status(first_responses, final_responses)
    # Export error_reports to CSV files and send them via mail
    export_directory = os.path.join(directory, "exported_reports")
    error_csv, valid_csv = export_reports_to_csv(error_reports, valid_reports, output_directory=export_directory)
    logging.info(f"Error reports saved to: {error_csv}")
    logging.info(f"Valid reports saved to: {valid_csv}")
    summary_report = []
   # Establish a database connection
    connection = connect_to_database()
    if connection:
        logging.info("Database connection established successfully.")
        # Here you can add code to interact with the database if needed
        if valid_reports:
           summary_report = update_db(connection, valid_reports)
        if error_reports:
           summary_report = update_db(connection, error_reports)
    else:
        logging.error("Failed to establish database connection.")
    connection.close()
    
    '''
    summery report contains:
    "report_id": report_id, (ie Mispar_divuah)
    "alert_id": alert_id,
    "status_divuah": status_divuah,
    "mispar_tkina": mispar_tkina
    '''
    #Update the alert in ActOne service with the new values

    session = login_and_get_session()

    if not session:
        logging.error("Failed to create or validate session")
        return  
    
    for report in summary_report:
        update_status = process_alert(session, report)
        if not update_status:
            logging.error(f"Failed to update alert for report: {report}")
            
        

if __name__ == "__main__":
    INPUT_DIR = "C:\\Users\\dvirbo\\Desktop\\mizrahi\\documents_20250527"
    main(INPUT_DIR)


    '''
    step 1: Parse XML files from the input directory
    step 2: Classify reports by status (error or valid) 
    step 3: Export classified reports to CSV files
    step 4: Establish a database connection
    step 5: update the 3 database tables with the reports
    step 6: connect to the ActOne service
    step 7: # TODO update the relevant feilds in the alert with the new values
    step 8: add_notes_request to the alert with the summary report
    step 9: # TODO send the error reports via email to the relevant recipients


    notes:
    when we got an error while tring to open a new client (like timeout), run this:
    #   Update certificates via pip
        pip install --upgrade certifi 
    
    '''
    

