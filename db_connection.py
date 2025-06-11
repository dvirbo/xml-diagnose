import pyodbc
import pandas as pd
import logging


server = 'IFS-LAB-2025'  # Your server name
database = 'master'  # Replace with your database name
username = 'sa'  # Replace with your SQL Server username
password = 'Mat1234!'  # Replace with your SQL Server password

def create_connection():
    insert_tables = ["IMP_REPORT_LOG", "ALERTS"]
    update_tables = ["IMP_REPORT_STATUS_TRACKING"]
    try:
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        connection = pyodbc.connect(connection_string)
        logging.info("Connection to SQL Server established successfully.")
        if connection:
            # Check if the required tables exist
            cursor = connection.cursor()
            for table in insert_tables + update_tables:
                cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}'")
                if not cursor.fetchone():
                    logging.warning(f"Table {table} does not exist in the database.")
            return connection


    except Exception as e:
        logging.error(f"Failed to connect to SQL Server: {e}")
        return None


