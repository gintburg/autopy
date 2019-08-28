"""Module with TestSuiteRedis class."""

from common.helpers import get_json_from_str
from rest.redis_storage.abstract_instance import AbstractRedisInstance
from rest.redis_storage.redis_client import RedisClient


class TestSuiteRedis(AbstractRedisInstance):
    """High level functional for work with Test suites hash in Redis storage.

    Test suite record schema (inside of hash):
        'id': "{title:<str>,length:<int>,cases:<list>}"

    Test suite data schema(used in responses):
        {
            id: unique identifier
            title: name of suite
            length : number of test cases in suite
            cases: list of linked test cases
        }
    """

    def __init__(self, hash_name):
        """:param hash_name: specific for test suites hash name"""
        self.__redis = RedisClient(hash_name)

    def get_record_data(self, suite_id):
        """Transform record data stored in Redis into dict.

        :param suite_id: id of test case
        :return: dict with test suite data (see schema in class docstring)
        """
        suite_data = get_json_from_str(self.__redis.get_item(suite_id))
        suite_data['id'] = suite_id

        return suite_data

    def add(self, data):
        """Add test suite to DB.

        :param data: dict with test suite data, schema :{title:<string>}
        :return: suite_id if successful, else None
        """
        suite_id = str(self.__redis.hash_len() + 1)
        suite_length = 0

        data = {
            "title": data['title'],
            "length": str(suite_length),
            "cases": []
        }

        result = self.__redis.set_item(suite_id, str(data))

        return suite_id if result else None

    def update(self, record_id, data):
        """Update test suite data.

        :param record_id: test case id
        :param data: dict with test suite data, schema :{title:<string>}
        :return: True if successful, else False
        """
        # Prepare data to be stored in DB
        suite_dict = get_json_from_str(self.__redis.get_item(record_id))

        data['length'] = suite_dict['length']
        data['cases'] = suite_dict['cases']

        return self.__redis.update_item(record_id, str(data))

    def get(self, suite_id):
        """Get test suite data from DB.

        :param suite_id: id of required suite data
        :return: dict with test suite data (see schema in class docstring)
        """
        if not self.__redis.is_item_exists(suite_id):
            return None

        return self.get_record_data(suite_id)

    def get_all(self):
        """Get data of all test suites.

        :return: list with suites data (see dicts schema in class docstring)
        """
        payload = []
        for suite_id in self.__redis.get_all_items().items():
            suite_data = self.get_record_data(suite_id)
            payload.append(suite_data)

        return payload

    def delete(self, suite_id):
        """Delete target test suite data.

        :param suite_id: id with required suite data
        :return: True if deleted successfully, else False
        """
        if self.__redis.is_item_exists(suite_id) and self.__redis.delete_item(
                suite_id):
            return True
        return False

    def delete_all(self):
        """Delete all test suites."""
        return self.__redis.delete_all_values()

    def is_item_exists(self, suite_id):
        """Verify that item exists.

        :param suite_id:
        :return: True if exists, else False
        """
        return self.__redis.is_item_exists(suite_id)

    def update_length(self, suite_id, action="+"):
        """Update suite length.

        :param suite_id: suite id
        :param action: + = increment; - = decrement
        """
        suite_data = get_json_from_str(self.__redis.get_item(suite_id))

        if action == "+":
            suite_data["length"] = int(suite_data["length"]) + 1
        elif action == "-":
            suite_data["length"] = int(suite_data["length"]) - 1
        else:
            raise RuntimeError(f"Unsupported action: '{action}'")

        self.__redis.update_item(suite_id, str(suite_data))

    def update_cases(self, suite_id, case_id, action='+'):
        """Update test case set that are linked to test suite.

        :param suite_id: id of test suite
        :param case_id: id of linked test case
        :param action: '+' - link test case, '-' unlink test case
        """
        suite_data = get_json_from_str(self.__redis.get_item(suite_id))

        if action == "+":
            suite_data["cases"].append(case_id)
        elif action == "-":
            suite_data["cases"].remove(case_id)
        else:
            raise RuntimeError(f"Unsupported action: '{action}'")

        self.__redis.update_item(suite_id, str(suite_data))
