"""Database connection management."""
import cx_Oracle as oracledb
from database.config import DB_CONFIG
from secure_password_store.password_manager import PasswordManager
from utils.config_loader import get_alerts_db_config


def connect_to_database():
    """Establish Oracle database connection using configuration.
    
    Uses Easy Connect String format (same as sqlplus):
    username/password@host:port/service_name
    """
    try:
        # Retrieve password using PasswordManager
        pm = PasswordManager()
        password = pm.get_password(DB_CONFIG['PASSWORD_KEY'])
        
        if not password:
            raise ValueError("Failed to retrieve database password using key: {}".format(DB_CONFIG['PASSWORD_KEY']))
        
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


def connect_to_alerts_database():
    """Establish Oracle database connection for ALERTS table (actone user).
    
    Uses Easy Connect String format (same as sqlplus):
    username/password@host:port/service_name
    """
    try:
        # Get alerts database configuration
        alerts_db_config = get_alerts_db_config()
        
        # Retrieve password using PasswordManager
        pm = PasswordManager()
        password = pm.get_password(alerts_db_config['PASSWORD_KEY'])
        
        if not password:
            raise ValueError("Failed to retrieve alerts database password using key: {}".format(alerts_db_config['PASSWORD_KEY']))
        
        # Use Easy Connect String format (same as sqlplus command line)
        # Format: username/password@host:port/service_name
        easy_connect_string = "{}/{}@{}:{}/{}".format(
            alerts_db_config['USERNAME'],
            password,
            alerts_db_config['HOST'],
            alerts_db_config['PORT'],
            alerts_db_config['SERVICE_NAME']
        )
        
        # Create connection using Easy Connect String
        connection = oracledb.connect(easy_connect_string)
        
        return connection
    except oracledb.Error as e:
        print("Alerts database connection failed: {}".format(e))
        return None
    except Exception as e:
        print("Unexpected error connecting to alerts database: {}".format(e))
        return None

