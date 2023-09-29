import json


class User:
    def __init__(self, redis_connection):
        self.redis = redis_connection

    def add_user(self, id, name):
        user_key = f"user:{id}"

        # Check if the user with the same ID already exists
        if self.redis.exists(user_key):
            return f"\nUser with ID {id} already exists."
        user_data = {
            "name": name
        }
        # Store the new user
        for field, value in user_data.items():
            self.redis.hset(user_key, field, value)
        return f"\nUser {name} created successfully."

    def get_all_users(self):
        user_keys = self.redis.keys("user:*")
        users = []
        for user_key in user_keys:
            key_type = self.redis.type(user_key).decode('utf-8')

            if key_type == 'hash':
                user_data = self.redis.hgetall(user_key)
                user_dict = {field.decode("utf-8"): value.decode("utf-8")
                             for field, value in user_data.items()}
                users.append(user_dict)
        return users

    def remove_user_by_id(self, id):
        user_key = f"user:{id}"
        user_data = self.redis.hgetall(user_key)
        if not self.redis.exists(user_key):
            return "\nUser not found."
        self.redis.delete(user_key)
        return "\nUser removed successfully."
