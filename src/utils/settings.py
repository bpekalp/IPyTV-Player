"""
Settings management for the IPTV Player
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    def __init__(self):
        self.app_name = "IPyTV-Player"
        self.settings_dir = self._get_settings_directory()
        self.settings_file = self.settings_dir / "settings.json"
        self.credentials_file = self.settings_dir / "credentials.json"
        
        # Ensure settings directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Default settings
        self.defaults = {
            'window': {
                'width': 1200,
                'height': 800,
                'maximized': False,
                'splitter_sizes': [300, 900]
            },
            'player': {
                'volume': 70,
                'auto_play': False,
                'hardware_acceleration': True,
                'buffer_size': 1024
            },
            'ui': {
                'theme': 'system',
                'show_epg': True,
                'show_thumbnails': True,
                'grid_view': False
            },
            'network': {
                'connection_timeout': 30,
                'read_timeout': 60,
                'retry_attempts': 3,
                'user_agent': 'IPyTV-Player/1.0'
            },
            'epg': {
                'auto_refresh': True,
                'refresh_interval': 6,  # hours
                'cache_duration': 24   # hours
            }
        }
        
        self._settings = self.defaults.copy()
        self.load_settings()
        
    def _get_settings_directory(self) -> Path:
        """Get platform-specific settings directory"""
        if os.name == 'nt':  # Windows
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif os.name == 'posix':
            if 'darwin' in os.sys.platform.lower():  # macOS
                base = Path.home() / 'Library' / 'Application Support'
            else:  # Linux
                base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        else:
            base = Path.home()
            
        return base / self.app_name
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self._merge_settings(loaded_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load settings: {e}")
            
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save settings: {e}")
            
    def _merge_settings(self, loaded_settings: Dict):
        """Merge loaded settings with defaults"""
        def merge_dict(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
            
        self._settings = merge_dict(self.defaults, loaded_settings)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value using dot notation (e.g., 'window.width')"""
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """Set setting value using dot notation"""
        keys = key.split('.')
        setting = self._settings
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in setting:
                setting[k] = {}
            setting = setting[k]
            
        # Set the value
        setting[keys[-1]] = value
        
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Load saved credentials"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load credentials: {e}")
        return None
        
    def save_credentials(self, server: str, username: str, password: str):
        """Save credentials (encrypted in production)"""
        credentials = {
            'server': server,
            'username': username,
            'password': password  # In production, this should be encrypted
        }
        
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
        except IOError as e:
            print(f"Failed to save credentials: {e}")
            
    def clear_credentials(self):
        """Clear saved credentials"""
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
        except IOError as e:
            print(f"Failed to clear credentials: {e}")
            
    def get_all_settings(self) -> Dict:
        """Get all settings"""
        return self._settings.copy()
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self._settings = self.defaults.copy()
        self.save_settings()
        
    def export_settings(self, file_path: str):
        """Export settings to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to export settings: {e}")
            
    def import_settings(self, file_path: str):
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                self._merge_settings(imported_settings)
                self.save_settings()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to import settings: {e}")

# Global settings instance
settings = Settings()