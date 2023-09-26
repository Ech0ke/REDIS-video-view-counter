import datetime
from redis.exceptions import WatchError
import time


class User_Video:
    def __init__(self, redis_connection):
        self.redis = redis_connection

    def watch_video(self, user_id, video_id):
        user_key = f"user:{user_id}"
        video_key = f"video:{video_id}"

        if not self.redis.exists(user_key):
            return f"\nUser with ID {user_id} not found."

        if not self.redis.exists(video_key):
            return f"\nVideo with ID {video_id} not found."
        # Queue the user to watch the video
        self.redis.rpush(f"video:{video_id}:watch_queue", user_id)

        # Wait for your turn in the queue
        while True:
            user_in_queue = (self.redis.lindex(
                f"video:{video_id}:watch_queue", 0)).decode('utf-8')
            if user_in_queue == user_id:
                break  # It's this user's turn
            else:
                time.sleep(1)  # Wait for 0.3 seconds before checking again

        # Start a Redis transaction using MULTI
        pipeline = self.redis.pipeline()

        try:
            # Watch the video's views field for changes
            pipeline.watch(video_key)

            # Increment the views count inside the transaction
            pipeline.multi()
            pipeline.hincrby(video_key, "views", 1)

            # # Increment views of the video
            pipeline.incr(f"{video_id}_incrementor")

            pipeline.sadd(f"user:{user_id}:watched_videos", video_key)

            user_video_data = {
                "fk_video_id": video_key,
                "fk_user_id": user_key,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            pipeline.sadd(f"user:{user_id}:video:{video_id}:watch_times",
                          user_video_data["time"])

            # for field, value in user_video_data.items():
            #     pipeline.hset(user_video_key, field, value)

            time.sleep(5)
            # Execute the transaction
            pipeline.execute()

            # Remove the user from the queue
            self.redis.lpop(f"video:{video_id}:watch_queue")

            return f"\n{user_id} watched video {video_id}."

        except WatchError:
            # Another client modified the video views field while we were trying to watch it
            return "Could not watch the video due to concurrent modification."

        finally:
            pipeline.reset()

    def get_watched_videos(self, user_id):
        watched_videos_key = f"user:{user_id}:watched_videos"
        watched_video_keys = self.redis.smembers(watched_videos_key)

        watched_videos = []

        for video_key in watched_video_keys:
            video_details = self.redis.hgetall(video_key)
            watched_videos.append(video_details)

        return watched_videos

    def remove_user_by_id(self, id):

        user_data = self.redis.get(f"user:{id}")
        if user_data == None:
            return "\nUser not found."
        self.redis.delete(f"user:{id}")
        return "\nUser removed successfully."
