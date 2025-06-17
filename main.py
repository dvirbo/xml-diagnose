import os
from db_connection import establish_sql_connection
from report_xml_classifier_v2 import classify_reports_by_status, export_reports_to_csv, parse_xml_files
import logging

logging.basicConfig(level=logging.INFO)

def main(directory: str) -> None:

    first_responses, final_responses = parse_xml_files(directory)
    error_reports, valid_reports = classify_reports_by_status(first_responses, final_responses)
    # Export error_reports to CSV files and send them via mail
    export_directory = os.path.join(directory, "exported_reports")
    error_csv, valid_csv = export_reports_to_csv(error_reports, valid_reports, output_directory=export_directory)
    logging.info(f"Error reports saved to: {error_csv}")
    logging.info(f"Valid reports saved to: {valid_csv}")
    # Establish a database connection
    connection = establish_sql_connection()
    if connection:
        logging.info("Database connection established successfully.")
        # Here you can add code to interact with the database if needed
        connection.close()
    else:
        logging.error("Failed to establish database connection.")


if __name__ == "__main__":
    INPUT_DIR = "C:\\Users\\dvirbo\\Desktop\\mizrahi\\documents_20250527"
    main(INPUT_DIR)