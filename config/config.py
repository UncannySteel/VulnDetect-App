import os
import json

CONFIG_PATH = os.path.join(os.environ.get('LOCALAPPDATA', os.getcwd()), 'AppCursor', 'config.json')

class Config:
    """
    Holds application configuration with sensible defaults.
    """
    def __init__(self, api_port=7869, db_path=None, theme='dark', auto_start_api=True, remote_url=''):
        self.api_port = api_port
        self.db_path = db_path or os.path.join(os.environ.get('LOCALAPPDATA', os.getcwd()), 'AppCursor', 'storage.db')
        self.theme = theme
        self.auto_start_api = auto_start_api
        self.remote_url = remote_url

    def to_dict(self):
        return {
            'api_port': self.api_port,
            'db_path': self.db_path,
            'theme': self.theme,
            'auto_start_api': self.auto_start_api,
            'remote_url': self.remote_url,
        }

    @staticmethod
    def from_dict(d):
        return Config(
            api_port=d.get('api_port', 7869),
            db_path=d.get('db_path'),
            theme=d.get('theme', 'dark'),
            auto_start_api=d.get('auto_start_api', True),
            remote_url=d.get('remote_url', ''),
        )

def get_config():
    """Load config from file or return defaults."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                return Config.from_dict(data)
        except Exception:
            pass
    return Config()

def save_config(config):
    """Save config to file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config.to_dict(), f, indent=2) 