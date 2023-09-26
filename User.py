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
        self.redis.set(user_key, json.dumps(user_data))
        return f"\nUser {name} created successfully."

    def get_all_users(self):
        user_keys = self.redis.keys("user:*")
        users = []
        for user_key in user_keys:
            user_data = self.redis.get(user_key)
            users.append(json.loads(user_data))
        return users

    def remove_user_by_id(self, id):

        user_data = self.redis.get(f"user:{id}")
        if user_data == None:
            return "\nUser not found."
        self.redis.delete(f"user:{id}")
        return "\nUser removed successfully."
