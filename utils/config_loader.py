"""Unified configuration loader for the entire project."""
import configparser
import os


_config_parser_instance = None
_config_dict_instance = None


def _load_config_parser():
    """Internal function to load ConfigParser instance."""
    global _config_parser_instance
    
    if _config_parser_instance is not None:
        return _config_parser_instance
    
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
    
    if not os.path.exists(config_file):
        raise FileNotFoundError("Configuration file not found: {}".format(config_file))
    
    _config_parser_instance = configparser.ConfigParser()
    _config_parser_instance.read(config_file)
    
    return _config_parser_instance


class ConfigDict:
    """Wrapper to make ConfigParser behave like a dict for backward compatibility."""
    def __init__(self, config_parser, section='general'):
        self._config = config_parser
        self._section = section
    
    def get(self, key, default=None):
        """Get a value from the general section."""
        try:
            return self._config.get(self._section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def __getitem__(self, key):
        """Get item like a dict."""
        return self.get(key)


def load_config():
    """
    Load configuration from config.ini file.
    Returns a dict-like object for backward compatibility with old config.json usage.
    """
    global _config_dict_instance
    
    if _config_dict_instance is not None:
        return _config_dict_instance
    
    config_parser = _load_config_parser()
    _config_dict_instance = ConfigDict(config_parser, section='general')
    
    return _config_dict_instance


def get_database_config():
    """
    Get database configuration as a dictionary.
    Returns dict with keys: HOST, PORT, SERVICE_NAME, USERNAME, PASSWORD, BATCH_SIZE, TIMEOUT
    """
    config = _load_config_parser()
    db_section = config['database']
    
    return {
        'HOST': db_section.get('host'),
        'PORT': db_section.get('port'),
        'SERVICE_NAME': db_section.get('service_name'),
        'USERNAME': db_section.get('username'),
        'PASSWORD': db_section.get('password'),
        'BATCH_SIZE': db_section.getint('batch_size', fallback=1000),
        'TIMEOUT': db_section.getint('timeout', fallback=30)
    }


def get_api_config():
    """
    Get API configuration as a dictionary (compatible with old api_config.json structure).
    """
    config = _load_config_parser()
    
    return {
        'api': {
            'base_url': config.get('api', 'base_url'),
            'endpoints': {
                'login': config.get('api', 'login_endpoint'),
                'logout': config.get('api', 'logout_endpoint')
            }
        },
        'credentials': {
            'username': config.get('credentials', 'username'),
            'password_key': config.get('credentials', 'password_key')
        },
        'logging': {
            'info_messages': {
                'login_success': config.get('logging', 'login_success'),
                'logout_success': config.get('logging', 'logout_success'),
                'password_debug': config.get('logging', 'password_debug')
            },
            'error_messages': {
                'login_failed': config.get('logging', 'login_failed'),
                'logout_failed': config.get('logging', 'logout_failed')
            }
        },
        'http': {
            'success_status_code': config.getint('http', 'success_status_code')
        },
        'main_messages': {
            'session_success': config.get('logging', 'session_success'),
            'session_failed': config.get('logging', 'session_failed')
        }
    }
