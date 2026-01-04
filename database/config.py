"""Database configuration - loads from unified config.ini file."""
from utils.config_loader import get_database_config

# Get database configuration from unified config.ini
_db_config = get_database_config()

DB_CONFIG = {
    'HOST': _db_config['HOST'],
    'PORT': _db_config['PORT'],
    'SERVICE_NAME': _db_config['SERVICE_NAME'],
    'USERNAME': _db_config['USERNAME'],
    'PASSWORD': _db_config['PASSWORD']
}

# Database settings
DB_SETTINGS = {
    'BATCH_SIZE': _db_config['BATCH_SIZE'],
    'TIMEOUT': _db_config['TIMEOUT']
}

