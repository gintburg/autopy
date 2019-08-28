"""Module with RedisClient class (contains basic Redis commands)."""

import redis


class RedisClient:
    """Redis Client handler.

    Creates Client object that allows to use basic Redis commands.
    All commands used in class are hash related.
    More info about Redis could be found in README.
    """

    def __init__(self, hash_name, host='localhost', port=6379):
        """__init__ obj.

        :param hash_name:   hash name of specific object (i.e."test_case_hash")
        :param host:    database’s hostname or IP address
        :param port:    database’s port
        """
        self.redis = redis.Redis(host=host, port=port)
        self.name = hash_name

    def set_item(self, key, value):
        """Add item to redis_storage database with "HSET" command.

        :return: True if set successfully, else False
        """
        if not self.is_item_exists(key):
            self.redis.hset(self.name, key, value)
            return True
        return False

    def update_item(self, key, value):
        """Update existing item in redis_storage database with "HSET" command.

        :return: True if updated successfully, else False
        """
        if self.is_item_exists(key):
            self.redis.hset(self.name, key, value)
            return True
        return False

    def get_item(self, key):
        """Get item from redis_storage database with "HGET" command.

        :return: field value if exists, else "Nil"
        """
        # Decode bytes into string
        return self.redis.hget(self.name, key).decode("utf-8")

    def get_all_items(self):
        """Get all items from redis_storage database with "HGETALL" command.

        :return: dict with fields and their values if exists, else {}
        """
        # Decode bytes into string
        return {key.decode("utf-8"): value.decode("utf-8") for key, value in
                self.redis.hgetall(self.name).items()}

    def delete_item(self, key):
        """Delete item from redis_storage database with "HDEL" command.

        :return: True if removed successfully, else False
        """
        return self.redis.hdel(self.name, key)

    def delete_all_values(self):
        """Delete all items with specific hash name with "HDEL" command.

        :return: True if removed successfully, else False
        """
        return bool(self.redis.delete(self.name))

    def hash_len(self):
        """Get length of items stored by specific hash name with "HLEN" command.

        :return: length (int)
        """
        return self.redis.hlen(self.name)

    def is_item_exists(self, key):
        """Verify item exists in redis_storage database with "HEXISTS" command.

        :return: True if exists, else False
        """
        return bool(self.redis.hexists(self.name, key))
