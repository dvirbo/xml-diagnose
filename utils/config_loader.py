"""Configuration loader utility."""
import json


def load_config():
    """Load configuration from config.json file."""
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

