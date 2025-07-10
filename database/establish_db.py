import pyodbc
from config import DB_CONFIG, CONNECTION_STRING_TEMPLATE

'''
try:
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    connection = pyodbc.connect(connection_string)
    logging.info("Connection to SQL Server established successfully.")
    return connection
'''

def get_connection_string():
    """Generate connection string from configuration."""
    return CONNECTION_STRING_TEMPLATE.format(**DB_CONFIG)

def connect_to_database():
    """Establish database connection using configuration."""
    try:
        connection_string = get_connection_string()
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        print(f"Database connection failed: {e}")
        return None
    
    

def main():
    connection = connect_to_database()
    if connection:
        print("Database connection established successfully.")
        # You can add more logic here, like executing a test query
        connection.close()
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()

