import pyodbc
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import DB_CONFIG, CONNECTION_STRING_TEMPLATE
from secure_password_store.password_manager import PasswordManager

def get_connection_string():
    """Generate connection string from configuration."""
    return CONNECTION_STRING_TEMPLATE.format(**DB_CONFIG) 

def connect_to_database():
    """Establish database connection using configuration."""
    try:
        pm = PasswordManager()
        password = pm.get_password("db_sa")
        
        # Add password to the config
        db_config = DB_CONFIG.copy()  # Make a copy to avoid modifying the original
        db_config['PASSWORD'] = password
        
        # Build connection string directly with all config including password
        connection_string = CONNECTION_STRING_TEMPLATE.format(**db_config)

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

