import os
import yaml

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
                with open(data, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            
            data = yaml.safe_load(data)
            if not isinstance(data, str):
                return data

            # file not found and input is not yaml, raise error
            raise FileNotFoundError(f"File not found: {data}")

        return data

    def __init__(self, config: str):
        # Look for the CONFIG environment variable, fallback to 'config.yml'
        self.config = Application.read(config)
