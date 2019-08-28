"""Config files handling."""

import os
import yaml


class Config:
    """Class to load YAML files from 'configs' dir."""

    configs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'configs')

    configs = {}

    for root, _, files in os.walk(configs_path):
        for file_name in files:
            if file_name.endswith('.yaml'):
                file_path = os.path.join(root, file_name)
                file_key = os.path.splitext(file_name)[0]
                if file_key in configs:
                    exception = f"Duplicate config name {file_key}!"
                    raise KeyError(exception)

                with open(file_path) as fconfig:
                    configs[file_key] = yaml.full_load(fconfig)

    @classmethod
    def get(cls, config_name='server_data'):
        """Return the config file by name.

        :param config_name: config file name
        :return: dict with config data
        """
        return cls.configs[config_name]
