"""Module with helpful for development functions."""

import json


def get_json_from_str(record):
    """Convert Redis record (str) into dict.

    :param record: record data that is stored in Redis
    :return: dict with record data
    """
    json_acceptable_string = record.replace("'", "\"")
    return json.loads(json_acceptable_string)
