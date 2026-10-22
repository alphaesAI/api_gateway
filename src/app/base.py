import logging
import os
import yaml
import json

logger = logging.getLogger(__name__)

class Application:
    '''

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
                    return yaml.safe_load(content)

            logger.info("Reading config from string content")
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return yaml.safe_load(data)

        logger.info("Using config object passed in memory")
        return data

    def __init__(self, config: str):
        self.config = Application.read(config)
        services = (self.config or {}).get("services", []) or (self.config or {}).get("cds_services", [])
        service_ids = [item.get("id") for item in services]
        logger.info("Config loaded services=%s", service_ids)