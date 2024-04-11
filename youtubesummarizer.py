from pytube import Search
from pytube import YouTube
from scenedetect import detect, ContentDetector

import imageio
from moviepy.editor import VideoFileClip

import os
import time

import easyocr


def search_for_videos(subject):

    print("Featching videos about", subject, " from youtube...")
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


def create_folder_based_on_current_time(subject):
    print("Creating summary folder...")
    current_time = time.strftime("%Y%m%d-%H%M%S")
    folder_name = f"video summary - {current_time} - {subject}"  # nopep8
    os.mkdir(folder_name)
    print("Summary folder: ", folder_name, "created successfully!")
    return folder_name


def download_video(video, folder_path):
    print("Top video: " + video.title)
    print("URL: " + video.watch_url)
    print("Downloading top video...")
    yt = YouTube(video.watch_url)
    video_path = yt.streams.get_highest_resolution().download(folder_path)
    print("Top video downloaded successfully!")
    return video_path


def scene_detection(video_path):
    print("Detecting scenes...")
    scene_list = detect(video_path, ContentDetector())
    print("Scenes detected successfully!")
    return scene_list


def parse_time(time_str):
    # Extracts the 'HH:MM:SS.MS' part and converts it to total seconds
    time_parts = time_str.split(' ')[0].split(':')
    hours, minutes, seconds = time_parts
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return total_seconds


def detect_text_with_easyocr(folder_path):
    print("Detecting text with easyocr in folder: ", folder_path)
    reader = easyocr.Reader(['en'])
    text_list = []
    for file in os.listdir(folder_path):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(folder_path, file)
            result = reader.readtext(file_path)
            if len(result) > 0:
                text_list.append(result)
    print(text_list)


def download_scene_frames(video_path, folder_path, scene_list, min_scene_length=1, images_num_from_scene=2):
    print("Downloading key scene frames...")

    video = VideoFileClip(video_path)

    for i, scene in enumerate(scene_list):
        # Parse the start and end times of the scene
        start_time = parse_time(str(scene[0]))
        end_time = parse_time(str(scene[1]))
        scene_length = end_time - start_time

        if scene_length < min_scene_length:
            continue

        for j in range(images_num_from_scene):
            time = start_time + (scene_length / (images_num_from_scene + 1)) * (j + 1)  # nopep8
            frame = video.get_frame(time)
            imageio.imwrite(f"{folder_path}/scene_{i + 1}_frame_{j + 1}.jpg", frame)  # nopep8

    print("Key scene frames downloaded successfully!")


def main():
    subject = input("Please enter a subject for the video: ")
    final_videos = search_for_videos(subject)
    top_video = final_videos[0]  # Top video
    print("---------------------------------")
    folder_path = create_folder_based_on_current_time(subject)
    print("---------------------------------")
    video_path = download_video(top_video, folder_path)
    print("---------------------------------")
    scene_list = scene_detection(video_path)
    print("---------------------------------")
    download_scene_frames(video_path, folder_path, scene_list)
    print("---------------------------------")
    detect_text_with_easyocr(folder_path)


if __name__ == "__main__":
    main()
