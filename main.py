import os
import logging
from db_usage import update_db,establish_sql_connection
from report_xml_classifier_v2 import classify_reports_by_status, export_reports_to_csv, parse_xml_files
from update_alert_soap import ActOne_login_and_get_session, add_notes_request

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
    alert_id = None
   # Establish a database connection
    connection = establish_sql_connection()
    if connection:
        logging.info("Database connection established successfully.")
        # Here you can add code to interact with the database if needed
        if valid_reports:
           summary_report, alert_id = update_db(connection, valid_reports)
        if error_reports:
           summary_report, alert_id = update_db(connection, error_reports)
    else:
        logging.error("Failed to establish database connection.")
    connection.close()

    client, session = ActOne_login_and_get_session()

    response  = add_notes_request(client, alert_id, summary_report, is_confidential=False)
    logging.info(f"Notes added to alert {alert_id}: {response}")
    # Close the session after all operations are done
    session.close()
    # send a summery reprt via addNotes service under 'alertsService'

    
    


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

    
    '''
    

