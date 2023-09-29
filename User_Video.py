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
            time.sleep(0.3)  # Wait for 0.3 seconds before checking again

        # Start a Redis transaction using MULTI
        pipeline = self.redis.pipeline()

        try:
            # Watch the video's views field for changes
            pipeline.watch(video_key)

            # Increment the views count inside the transaction
            pipeline.multi()
            pipeline.hincrby(video_key, "views", 1)

            # Increment views of the video
            pipeline.incr(f"{video_id}_incrementor")
            # Associate user with watched video
            pipeline.sadd(f"user:{user_id}:watched_videos", video_key)

            video_view_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Register the time of watched video and associate it with the user
            pipeline.sadd(f"user:{user_id}:video:{video_id}:watch_times",
                          video_view_time)

            # Associate user id video the video
            pipeline.sadd(f"video:{video_id}:viewers", user_id)

            # time.sleep(5)
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

        if not self.redis.exists(watched_videos_key):
            return f"\nUser with ID {user_id} not found or he/she didn't watch any videos."

        watched_video_keys = self.redis.smembers(watched_videos_key)

        watched_videos = []

        for video_key_bytes in watched_video_keys:
            video_key = video_key_bytes.decode(
                'utf-8')  # Decode the bytes to a string
            video_details = self.redis.hgetall(video_key)

            # Decode the "name" and "views" fields
            video_details_decoded = {
                key.decode('utf-8'): value.decode('utf-8') for key, value in video_details.items()
            }

            watch_times = self.get_watch_times(user_id, video_key)

            for time in watch_times:
                video_details_decoded["Time"] = time
                # Use copy to avoid overwriting
                watched_videos.append(video_details_decoded.copy())

        return watched_videos

    def get_viewers(self, video_id):
        viewers_key = f"video:{video_id}:viewers"
        viewer_data = []

        if not self.redis.exists(viewers_key):
            return f"\nVideo with id {video_id} doesn't exist or no one has watched the video yet"

        viewer_ids = self.redis.smembers(viewers_key)
        for viewer_id_bytes in viewer_ids:
            viewer_id = viewer_id_bytes.decode(
                'utf-8')  # Decode the bytes to a string
            viewer_name = self.redis.hget(
                f"user:{viewer_id}", "name").decode('utf-8')
            viewer_watch_times = self.get_watch_times(
                viewer_id, f"video:{video_id}")

            for time in viewer_watch_times:
                viewer_data.append({
                    "UserId": viewer_id,
                    "UserName": viewer_name,
                    "Time": time,
                })

        return viewer_data

    def get_watch_times(self, user_id, video_key):
        print(user_id)
        watch_times_key = f"user:{user_id}:{video_key}:watch_times"
        watch_times = self.redis.smembers(watch_times_key)

        # Decode the bytes to strings
        return [time.decode('utf-8') for time in watch_times]
