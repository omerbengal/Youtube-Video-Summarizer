from pytube import Search
from pytube import YouTube
from scenedetect import detect, ContentDetector


def search_for_videos(subject):

    print("Featching videos...")
    search = Search(subject)

    final_videos = [
        video for video in search.results if video.length / 60 < 10]

    if len(final_videos) == 0:
        print("No videos that are shorte than 10 minutes found. Fetching more videos...")
        search.results
        search.get_next_results()
        final_videos = [
            video for video in search.results if video.length / 60 < 10]
        if len(final_videos) == 0:
            print("No videos that are shorte than 10 minutes found. Exiting...")
            exit()

    # Sort list of videos by views in descending order
    # final_videos.sort(key=lambda x: x.views, reverse=True)
    print("Videos fetched successfully!")
    return final_videos


def download_video(video):
    print("Downloading top video...")
    yt = YouTube(video.watch_url)
    print("Top video: " + yt.title)
    print("URL: " + yt.watch_url)
    return yt.streams.get_highest_resolution().download()

# for i in range(len(final_videos)):
#     print("video #" + str(i) + " - title: " + final_videos[i].title)
#     print("video #" + str(i) + " - url: " + final_videos[i].watch_url)
#     print("video #" + str(i) + " - length: " +
#           str(final_videos[i].length) + " seconds or " + str(final_videos[i].length / 60) + " minutes")
#     # print("video #" + str(i) + " - rating: " + str(final_videos[i].rating))
#     print("video #" + str(i) + " - views: " +
#           str(format(final_videos[i].views, ",")))


def scene_detection(video_path):
    print("Detecting scenes...")
    scene_list = detect(video_path, ContentDetector())
    print(scene_list)


def main():
    subject = input("Please enter a subject for the video: ")
    top_video = search_for_videos(subject)[0]
    video_path = download_video(top_video)
    scene_detection(video_path)


if __name__ == "__main__":
    main()
