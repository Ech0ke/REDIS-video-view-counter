import redis
from User import User
from Video import Video
from User_Video import User_Video


def main():
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.flushdb()
    # Define the Video entity
    # video1 = {
    #     "id": r.incr("video_id"),  # Auto-generated ID
    #     "name": "Video 1",
    #     "views": 1000
    # }

    # # Define the User entity
    # user1 = {
    #     "id": r.incr("user_id"),  # Auto-generated ID
    #     "name": "User 1"
    # }

    # # Define the Video-User entity
    # video_user1 = {
    #     "id": r.incr("video_user_id"),  # Auto-generated ID
    #     "video_id": video1["id"],
    #     "user_id": user1["id"],
    #     "time": "2023-09-24 12:00:00"  # Use a valid date and time
    # }

    # # Store entities in Redis as JSON strings
    # r.set(f"video:{video1['id']}", json.dumps(video1))
    # r.set(f"user:{user1['id']}", json.dumps(user1))
    # r.set(f"video_user:{video_user1['id']}", json.dumps(video_user1))

    user_manager = User(r)
    video_manager = Video(r)
    user_video_manager = User_Video(r)

    user_manager.add_user("Jonas123", "Jonas")
    user_manager.add_user("PetrasV", "Petras")

    video_manager.add_video(
        "video1", "Elon Musk vs Zucc LIVE fight (NOT CLICKBAIT)")
    video_manager.add_video("video2", "Aliens found")
    video_manager.add_video("video3", "Why you suck at coding?")

    while True:
        print("\nVideo platform")
        print("---------------------")
        print("1. Add user")
        print("2. Show all users")
        print("3. Remove user by id")
        print("4. Add video")
        print("5. Show all videos")
        print("6. Remove video by id")
        print("7. Watch video")
        print("8. Show watched videos by user")
        print("8. Show all users by video")
        print("9. Exit")
        print("---------------------")

        choice = input("Enter your choice (1-9): ")

        match choice:
            case "1":
                user_id = input("Enter user id: ")
                user_name = input("Enter user name: ")
                message = user_manager.add_user(user_id, user_name)
                print(message)

            case "2":
                all_users = user_manager.get_all_users()
                print("\nAll users:\n")
                for user in all_users:
                    print(f"{user['name']}")
            case "3":
                user_id = input("Enter user id: ")
                result = user_manager.remove_user_by_id(user_id)
                print(result)
            case "4":
                video_id = input("Enter video id: ")
                video_name = input("Enter video name: ")
                message = video_manager.add_video(video_id, video_name)
                print(message)
            case "5":
                all_videos = video_manager.get_all_videos()
                print("\nAll videos:\n")
                print("{:<80} {:<10}".format("Name", "Views"))
                for video in all_videos:
                    print("{:<80} {:<10}".format(
                        video['name'], video['views']))
            case "6":
                video_id = input("Enter video id: ")
                result = video_manager.remove_video_by_id(video_id)
                print(result)
            case "7":
                user_id = input(
                    "Enter the user ID of the person who will watch the video: ")
                video_id = input("Enter video id: ")
                message = user_video_manager.watch_video(user_id, video_id)
                print(message)
            case "8":
                user_id = input(
                    "Enter user id to view all of his/her watched videos: ")
                result = user_video_manager.get_watched_videos(user_id)
                print(result)
            case "9":
                print("Application shutdown")
                break
            case _:
                print("Invalid choice! Please choose a valid option.")


if __name__ == "__main__":
    main()
