import datetime
from redis.exceptions import WatchError
import time


class User_Video:
    def __init__(self, redis_connection):
        self.redis = redis_connection

    def watch_video(self, user_id, video_id):
        user_key = f"user:{user_id}"
        video_key = f"video:{video_id}"

        # Check if user exists
        if not self.redis.exists(user_key):
            return f"\nUser with ID {user_id} not found."
        # Check if video exists
        if not self.redis.exists(video_key):
            return f"\nVideo with ID {video_id} not found."

        # Queue the user to watch the video
        self.redis.rpush(f"video:{video_id}:watch_queue", user_id)

        # Wait for user's turn in the queue
        while True:
            user_in_queue = (self.redis.lindex(
                f"video:{video_id}:watch_queue", 0)).decode('utf-8')
            # if user is first in queue, then break off the loop
            if user_in_queue == user_id:
                break
            # Wait for 0.3 seconds before checking queue position again
            time.sleep(0.3)

        # Start a Redis transaction
        pipeline = self.redis.pipeline()

        try:
            # Watch the video's views field for changes
            pipeline.watch(video_key)

            # Increment the views count column inside video hash
            pipeline.multi()
            pipeline.hincrby(video_key, "views", 1)

            # Append video key as value to user watched videos set
            pipeline.sadd(f"user:{user_id}:watched_videos", video_key)

            # Get the current time as string
            video_view_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Register the time of watched video and associate it with the user
            pipeline.sadd(f"user:{user_id}:video:{video_id}:watch_times",
                          video_view_time)

            # Append user id as value to video viewers set
            pipeline.sadd(f"video:{video_id}:viewers", user_id)

            # Artificially slow down the transaction
            # time.sleep(10)
            # Execute the transaction
            pipeline.execute()

            # Remove the user from the queue
            self.redis.lpop(f"video:{video_id}:watch_queue")

            # Return success message
            return f"\n{user_id} watched video {video_id}."

        except WatchError:
            # Another client modified the video views field while we were trying to watch it and video queue didn't initiate properly
            return "Could not watch the video due to concurrent modification."
        # Cleanup
        finally:
            pipeline.reset()

    def get_watched_videos(self, user_id):
        watched_videos_key = f"user:{user_id}:watched_videos"
        # Check if user watched any videos
        if not self.redis.exists(watched_videos_key):
            return f"\nUser with ID {user_id} not found or he/she didn't watch any videos."
        # Retrieve all watched video keys
        watched_video_keys = self.redis.smembers(watched_videos_key)

        # Initiate array that will store all video info
        watched_videos = []

        for video_key_bytes in watched_video_keys:
            # Decode the bytes to a string
            video_key = video_key_bytes.decode(
                'utf-8')
            # Get video hash fields as bytes object
            video_details = self.redis.hgetall(video_key)
            # Decode the "name" and "views" fields
            video_details_decoded = {
                key.decode('utf-8'): value.decode('utf-8') for key, value in video_details.items()
            }
            # Extract all watch times of current watched video being looped through
            watch_times = self.get_watch_times(user_id, video_key)

            # Append all video watch times to object
            for time in watch_times:
                video_details_decoded["Time"] = time
                # Use copy to avoid overwriting
                watched_videos.append(video_details_decoded.copy())

        return watched_videos

    def get_viewers(self, video_id):
        viewers_key = f"video:{video_id}:viewers"
        viewer_data = []
        # Check if video has been watched by anyone
        if not self.redis.exists(viewers_key):
            return f"\nVideo with ID {video_id} doesn't exist or no one has watched the video yet"

        # Retrieve all user ids that watched the video
        viewer_ids = self.redis.smembers(viewers_key)

        for viewer_id_bytes in viewer_ids:
            # Decode the bytes to a string
            viewer_id = viewer_id_bytes.decode(
                'utf-8')

            # Get viewer name
            viewer_name = self.redis.hget(
                f"user:{viewer_id}", "name").decode('utf-8')

            # Get all watch times of that viewer
            viewer_watch_times = self.get_watch_times(
                viewer_id, f"video:{video_id}")
            # Form object to return
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

        # Decode bytes to strings
        return [time.decode('utf-8') for time in watch_times]
