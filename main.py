import redis
from User import User
from Video import Video
from User_Video import User_Video


def main():
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.flushdb()

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
        print("3. Remove user by ID")
        print("4. Add video")
        print("5. Show all videos")
        print("6. Remove video by ID")
        print("7. Watch video")
        print("8. Show watched videos by user ID")
        print("9. Show all user's watch times by video ID")
        print("10. Exit")
        print("---------------------")

        choice = input("Enter your choice (1-10): ")

        match choice:
            case "1":
                user_id = input("Enter user ID: ")
                user_name = input("Enter user name: ")
                message = user_manager.add_user(user_id, user_name)
                print(message)

            case "2":
                all_users = user_manager.get_all_users()
                print("\nAll users:\n")
                for user in all_users:
                    print(f"{user['name']}")
            case "3":
                user_id = input("Enter user ID: ")
                result = user_manager.remove_user_by_id(user_id)
                print(result)
            case "4":
                video_id = input("Enter video ID: ")
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
                video_id = input("Enter video ID: ")
                result = video_manager.remove_video_by_id(video_id)
                print(result)
            case "7":
                user_id = input(
                    "Enter the user ID of the person who will watch the video: ")
                video_id = input("Enter video ID: ")
                message = user_video_manager.watch_video(user_id, video_id)
                print(message)
            case "8":
                user_id = input(
                    "Enter user ID to view all of his/her watched videos: ")
                user_watched_videos = user_video_manager.get_watched_videos(
                    user_id)
                if isinstance(user_watched_videos, list):
                    # If user_watched_videos is a list (array)
                    print("\n")
                    print("{:<80} {:<10} {:<15}".format(
                        "Video Name", "Views", "Time"))
                    for video in user_watched_videos:
                        print("{:<80} {:<10} {:<15}".format(
                            video['name'], video['views'], video['Time']))
                elif isinstance(user_watched_videos, str):
                    # If user_watched_videos is a string
                    print(user_watched_videos)
            case "9":
                video_id = input(
                    "Enter video ID to view all users that watched this video: ")
                video_viewers = user_video_manager.get_viewers(
                    video_id)
                if isinstance(video_viewers, list):
                    # If user_watched_videos is a list (array)
                    print("\n")
                    print("{:<30} {:<30} {:<10}".format(
                        "User ID", "User Name", "Time"))
                    for viewer in video_viewers:
                        print("{:<30} {:<30} {:<10}".format(
                            viewer['UserId'],
                            viewer['UserName'], viewer['Time']))
                elif isinstance(video_viewers, str):
                    # If user_watched_videos is a string
                    print(video_viewers)
            case "10":
                print("Application shutdown")
                break
            case _:
                print("Invalid choice! Please choose a valid option.")


if __name__ == "__main__":
    main()
