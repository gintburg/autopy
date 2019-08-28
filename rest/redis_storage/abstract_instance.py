"""Module with AbstractRedisInstance class."""

from abc import ABC, abstractmethod


class AbstractRedisInstance(ABC):
    """Abstract class for Redis instance classes (high level)."""

    @abstractmethod
    def get_record_data(self, record_id):
        """Transform record data stored in Redis (str) into dict.

        :param record_id: id or the record
        """
        pass

    @abstractmethod
    def add(self, data):
        """Add data into instance.

        :param data: data in appropriate for Redis instance format
        """
        pass

    @abstractmethod
    def update(self, record_id, data):
        """Update instance data.

        :param record_id: id of the updating record
        :param data: data in appropriate for Redis instance format
        """
        pass

    @abstractmethod
    def get(self, record_id):
        """Get record data by id.

        :param record_id: record id with required data
        """
        pass

    @abstractmethod
    def get_all(self):
        """Get data for all existing test cases."""
        pass

    @abstractmethod
    def delete(self, record_id):
        """Delete record from instance.

        :param record_id: id od required record.
        """
        pass

    @abstractmethod
    def delete_all(self):
        """Delete all test cases."""
        pass

    @abstractmethod
    def is_item_exists(self, record_id):
        """Verify that item exists inside of instance.

        :param record_id: id of the record
        """
        pass
