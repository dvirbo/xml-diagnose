"""Database connection management."""
import pyodbc
from database.config import DB_CONFIG, CONNECTION_STRING_TEMPLATE
from secure_password_store.password_manager import PasswordManager


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
        print("Database connection failed: {}".format(e))
        return None

