"""Module with TestCaseRedis class."""

from common.helpers import get_json_from_str
from rest.redis_storage.abstract_instance import AbstractRedisInstance
from rest.redis_storage.redis_client import RedisClient


class TestCaseRedis(AbstractRedisInstance):
    """High level functional for work with Test cases hash in Redis storage.

    Test case record schema (inside of hash):
        "id": "{suite_id:<str>,title:<str>,description:<strt>}"

    Test case data schema (used in responses):
        {
            id: unique identifier
            suites_id: connection to suite
            title: test case name
            description: short info about test case
        }
    """

    def __init__(self, hash_name):
        """:param hash_name: specific for test cases hash name."""
        self.__redis = RedisClient(hash_name)

    def get_record_data(self, case_id):
        """Transform record data stored in Redis into dict.

        :param case_id: id of test case
        :return: dict with test case data (see schema in class docstring)
        """
        suite_data = get_json_from_str(self.__redis.get_item(case_id))
        suite_data['id'] = case_id

        return suite_data

    def add(self, data):
        """Add test case data into DB.

        :param data: test case data, schema:
                {
                    suites_id: connection to suite
                    title: test case name
                    description: short info about test case
                }
        :return: case_id if successful, else None
        """
        # Calculate id for test case data
        case_id = str(self.__redis.hash_len() + 1)

        result = self.__redis.set_item(case_id, str(data))

        return case_id if result else None

    def update(self, case_id, data):
        """Update test case data.

        :param case_id: test case id
        :param data: test case data, schema:
                {
                    suites_id: connection to suite
                    title: test case name
                    description: short info about test case
                }
        :return: True if successful, else False
        """
        return self.__redis.update_item(case_id, str(data))

    def get(self, case_id):
        """Get test case data by id.

        :param case_id: test case id with required data
        :return: dict with test case data (see schema in class docstring)
        """
        if not self.__redis.is_item_exists(case_id):
            return None

        return self.get_record_data(case_id)

    def get_all(self):
        """Get data for all existing test cases.

        :return: list with test cases data(see dicts schema in class docstring)
        """
        payload = []
        for case_id in self.__redis.get_all_items().items():
            data = self.get_record_data(case_id)
            payload.append(data)

        return payload

    def delete(self, case_id):
        """Delete test case.

        :param case_id: id for required test case data
        :return: True if removed successfully, else False
        """
        if self.__redis.is_item_exists(case_id) and \
                self.__redis.delete_item(case_id):
            return True

        return False

    def delete_all(self):
        """Delete all test cases."""
        return self.__redis.delete_all_values()

    def is_item_exists(self, case_id):
        """Verify that item exists.

        :param case_id: id of the test case
        :return: True if exists, else False
        """
        return self.__redis.is_item_exists(case_id)

    def get_suite_id(self, case_id):
        """Get suite id for specific test case.

        :return: suite id (int)
        """
        case_data = get_json_from_str(self.__redis.get_item(case_id))
        return int(case_data['suite_id'])
