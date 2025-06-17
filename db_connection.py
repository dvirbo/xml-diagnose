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


