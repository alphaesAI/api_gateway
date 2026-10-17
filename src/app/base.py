import logging
import os
import yaml

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
                    return yaml.safe_load(f)

            logger.info("Reading config from a YAML string")
            data = yaml.safe_load(data)
            if not isinstance(data, str):
                return data

            logger.error("Config file not found: %s", data)
            raise FileNotFoundError(f"File not found: {data}")

        logger.info("Using config object passed in memory")
        return data

    def __init__(self, config: str):
        self.config = Application.read(config)
        service_ids = [item.get("id") for item in (self.config or {}).get("cds_services", [])]
        logger.info("Config loaded services=%s", service_ids)
