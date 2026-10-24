import logging
import os
import yaml
import json

logger = logging.getLogger(__name__)

class Application:
    '''
    Base application class for all applications
    '''

    @staticmethod
    def read(data):
        '''
        Read data from file or string

        Args:
            data (str): file path or yaml string

        Returns:
            dict: configuration
        '''
        if isinstance(data, str):
            if os.path.exists(data):
                logger.info("Reading config file %s", data)
                with open(data, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if data.endswith('.json'):
                        return json.loads(content)
                    
                    # If it's a YAML file, also look for a companion services.json in the same folder
                    config_data = yaml.safe_load(content) or {}
                    base_dir = os.path.dirname(data)
                    json_path = os.path.join(base_dir, "services.json")
                    if os.path.exists(json_path):
                        logger.info("Loading companion service registry %s", json_path)
                        with open(json_path, 'r', encoding='utf-8') as jf:
                            json_data = json.load(jf)
                            config_data.update(json_data)
                    return config_data

            logger.info("Reading config from string content")
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return yaml.safe_load(data)

        return data

    def __init__(self, config: str):
        self.config = Application.read(config)
        services = (self.config or {}).get("services", []) or (self.config or {}).get("cds_services", [])
        service_ids = [item.get("id") for item in services]
        logger.info("Config loaded services=%s", service_ids)