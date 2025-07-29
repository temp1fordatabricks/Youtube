import os
import json
from pathlib import Path

class Config:
    """
    Configuration manager for the YouTube Content Optimization app.
    """
    
    def __init__(self):
        self.config_file = Path("app_config.json")
        self.config = self.load_config()
    
    def load_config(self):
        """
        Load configuration from file or create default configuration.
        """
        default_config = {
            "api_keys": {
                "perplexity": ""
            },
            "export_settings": {
                "default_format": "txt",
                "auto_export": False
            },
            "ui_settings": {
                "theme": "light",
                "window_size": [800, 600]
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """
        Save configuration to file.
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_api_key(self, service):
        """
        Get API key for a service.
        
        Args:
            service (str): Service name (e.g., 'perplexity')
        
        Returns:
            str: API key or empty string if not found
        """
        # First check environment variable
        env_key = os.environ.get(f"{service.upper()}_API_KEY")
        if env_key:
            return env_key
        
        # Then check config file
        return self.config.get("api_keys", {}).get(service, "")
    
    def set_api_key(self, service, api_key):
        """
        Set API key for a service.
        
        Args:
            service (str): Service name (e.g., 'perplexity')
            api_key (str): API key to set
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        
        self.config["api_keys"][service] = api_key
        self.save_config()
    
    def get_export_setting(self, setting):
        """
        Get export setting.
        
        Args:
            setting (str): Setting name
        
        Returns:
            Value of the setting
        """
        return self.config.get("export_settings", {}).get(setting)
    
    def set_export_setting(self, setting, value):
        """
        Set export setting.
        
        Args:
            setting (str): Setting name
            value: Value to set
        """
        if "export_settings" not in self.config:
            self.config["export_settings"] = {}
        
        self.config["export_settings"][setting] = value
        self.save_config()
    
    def get_ui_setting(self, setting):
        """
        Get UI setting.
        
        Args:
            setting (str): Setting name
        
        Returns:
            Value of the setting
        """
        return self.config.get("ui_settings", {}).get(setting)
    
    def set_ui_setting(self, setting, value):
        """
        Set UI setting.
        
        Args:
            setting (str): Setting name
            value: Value to set
        """
        if "ui_settings" not in self.config:
            self.config["ui_settings"] = {}
        
        self.config["ui_settings"][setting] = value
        self.save_config()

# Global config instance
config = Config()