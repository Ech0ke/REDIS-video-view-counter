import json


class Video:
    def __init__(self, redis_connection):
        self.redis = redis_connection

    def add_video(self, id, name):
        video_key = f"video:{id}"

        # Check if the video with the same ID already exists
        if self.redis.exists(video_key):
            return f"\nVideo with ID {id} already exists."
        video_data = {
            "name": name,
            "views": 0
        }
        # Store new video
        for field, value in video_data.items():
            self.redis.hset(video_key, field, value)
        return f"\nVideo {name} created successfully."

    def get_all_videos(self):
        video_keys = self.redis.keys("video:*")
        videos = []
        for video_key in video_keys:
           # Get key data type
            key_type = self.redis.type(video_key).decode('utf-8')
            # Check for key type in order to collect video info and not video's viewers
            if key_type == 'hash':
                video_data = self.redis.hgetall(video_key)
                video_dict = {field.decode("utf-8"): value.decode("utf-8")
                              for field, value in video_data.items()}
                videos.append(video_dict)
        return videos

    def remove_video_by_id(self, id):
        video_key = f"video:{id}"
        if not self.redis.exists(video_key):
            return f"\nVideo {id} not found."
        self.redis.delete(video_key)
        return f"\nVideo {id} removed successfully."
