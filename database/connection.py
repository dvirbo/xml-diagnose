"""Database connection management."""
import cx_Oracle as oracledb
from database.config import DB_CONFIG
from secure_password_store.password_manager import PasswordManager


def connect_to_database():
    """Establish Oracle database connection using configuration.
    
    Uses Easy Connect String format (same as sqlplus):
    username/password@host:port/service_name
    """
    try:
        # Use password from config directly
        # Note: We skip secure storage for Oracle since credentials are in config
        password = DB_CONFIG['PASSWORD']
        
        # Use Easy Connect String format (same as sqlplus command line)
        # Format: username/password@host:port/service_name
        easy_connect_string = "{}/{}@{}:{}/{}".format(
            DB_CONFIG['USERNAME'],
            password,
            DB_CONFIG['HOST'],
            DB_CONFIG['PORT'],
            DB_CONFIG['SERVICE_NAME']
        )
        
        # Create connection using Easy Connect String
        connection = oracledb.connect(easy_connect_string)
        
        return connection
    except oracledb.Error as e:
        print("Database connection failed: {}".format(e))
        return None
    except Exception as e:
        print("Unexpected error connecting to database: {}".format(e))
        return None

