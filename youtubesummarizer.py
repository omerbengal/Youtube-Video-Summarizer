from pytube import Search
from pytube import YouTube
from scenedetect import detect, ContentDetector

import imageio
from moviepy.editor import VideoFileClip

import os
import time

import easyocr

from PIL import Image, ImageDraw, ImageFont, ImageTk

import re

import tkinter as tk


def search_for_videos(subject):
    print("Fetching videos about ", subject, " from YouTube...")
    search = Search(subject)
    final_videos = [video for video in search.results if video.length / 60 < 10]  # nopep8

    if len(final_videos) == 0:
        print("No videos that are shorter than 10 minutes found. Fetching more videos...")

        if len(final_videos) == 0:
            print("No videos that are shorter than 10 minutes found. Exiting...")
            exit(0)

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
    scene_list = detect(video_path, ContentDetector(threshold=45))
    print("Scenes detected successfully!")
    return scene_list


def parse_time(time_str):
    # Extracts the 'HH:MM:SS.MS' part and converts it to total seconds
    time_parts = time_str.split(' ')[0].split(':')
    hours, minutes, seconds = time_parts
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return total_seconds


def download_scene_frames(video_path, folder_path, scene_list, min_scene_length=1, images_num_from_scene=3):
    print("Downloading " + str(len(scene_list)) + " key scene frames...")

    video = VideoFileClip(video_path)

    if scene_list is None or len(scene_list) == 0:
        print("No scenes detected - downloading the middle frame of the video...")
        frame = video.get_frame(video.duration / 2)
        imageio.imwrite(f"{folder_path}/scene_1_frame_1.jpg", frame)
    else:
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


def detect_text_with_easyocr(folder_path):
    print("Detecting text with easyocr in:", folder_path)
    reader = easyocr.Reader(['en'])
    text_list = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.jpg', '.png', 'jpeg')):
            file_path = os.path.join(folder_path, file)
            result = reader.readtext(file_path)
            if len(result) > 0:
                for detection in result:
                    text = detection[1]
                    text_list.append(text)
    print("Text detected successfully!")
    return text_list


def add_watermark_to_images(folder_path, watermark_text="Omer Bengal"):

    print("Adding watermark to images in: ", folder_path)
    images_paths = []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', 'jpeg'))]  # nopep8

    # Loop through all files in the input folder
    for i, filename in enumerate(files):
        image_path = os.path.join(folder_path, filename)
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        # Font settings (size, color, etc.)

        # Dynamic font size based on image size
        font_size = int(min(image.size) / 20)
        font = ImageFont.truetype("Rubik-Regular.ttf", font_size)

        # Calculate text width and approximate height
        text_width = draw.textlength(watermark_text, font=font)
        text_height = font_size  # Approximate height based on font size
        x = image.width - text_width - 10  # 10 pixels from the right edge
        y = image.height - text_height - 10  # 10 pixels from the bottom edge

        # text color based on the avg brightness of the area where the text will be placed
        brightnesses_list = []
        for x_temp in range(int(image.width - text_width), int(image.width)):
            for y_temp in range(int(image.height - text_height), int(image.height)):
                R, G, B = image.getpixel((x_temp, y_temp))
                brightness = (0.2126 * R) + (0.7152 * G) + (0.0722 * B)
                brightnesses_list.append(brightness)

        avg_brightness = sum(brightnesses_list) / len(brightnesses_list)
        text_color = (0, 0, 0) if avg_brightness > 128 else (255, 255, 255)

        # Add text to image
        draw.text((x, y), watermark_text, font=font, fill=text_color)

        # Save the watermarked image
        output_path = os.path.join(folder_path, filename)
        images_paths.append(output_path)
        image.save(output_path)

    print("Watermark added to images successfully!")
    return images_paths


def extract_scene_and_frame(filename):
    # Regular expression to find the pattern `scene_NUMBER_frame_NUMBER`
    match = re.search(r'scene_(\d+)_frame_(\d+)', filename)
    if match:
        # Return the scene and frame numbers as a tuple of integers
        return int(match.group(1)), int(match.group(2))
    return 0, 0  # Default return if no match is found


def create_gif_from_images(subject, images_paths, folder_path):
    print("Creating GIF from images...")
    images = []
    for i, image_path in enumerate(images_paths):
        images.append(imageio.imread(image_path))

    gif_output_path = os.path.join(folder_path, (subject + " - summary.gif"))
    # determine the fps based on the number of images and the need for the gif to be max 10 sec
    fps_based_on_images_num_and_10_sec_gif = 3 if len(images) / 3 < 10 else int(len(images) / 10)  # nopep8
    imageio.mimsave(gif_output_path, images, format='GIF', fps=fps_based_on_images_num_and_10_sec_gif)  # nopep8
    print("GIF created successfully!")
    return gif_output_path


def animation(photoimage_objects, gif_label, frames, current_frame=0):
    global loop
    image = photoimage_objects[current_frame]

    gif_label.configure(image=image)
    current_frame = current_frame + 1

    if current_frame == frames:
        current_frame = 0

    # the video should be 10 sec max
    fps_based_on_images_num_and_10_sec_gif = 3 if frames / 3 < 10 else int(frames / 10)  # nopep8

    loop = tk_root.after(int(1000 / fps_based_on_images_num_and_10_sec_gif), lambda: animation(photoimage_objects, gif_label, frames, current_frame))  # nopep8


def display_gif_with_gui(gif_output_path):
    print("Displaying GIF...")
    global tk_root
    tk_root = tk.Tk()  # Create a GUI window object using Tkinter
    tk_root.title("Displaing Gif")
    gif_info = Image.open(gif_output_path)
    frames = gif_info.n_frames  # number of frames

    photoimage_objects = []
    for i in range(frames):
        gif_info.seek(i)
        obj = ImageTk.PhotoImage(gif_info)
        photoimage_objects.append(obj)

    gif_label = tk.Label(tk_root, image="")
    gif_label.pack()

    animation(photoimage_objects, gif_label, frames, current_frame=0)

    tk_root.mainloop()

    print("GIF displayed successfully! Have a good day :)")


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
    text_list = detect_text_with_easyocr(folder_path)
    print('concatination of detected texts: ', ''.join(text_list))
    print("---------------------------------")
    images_paths = add_watermark_to_images(folder_path)
    images_paths_sorted = sorted(images_paths, key=extract_scene_and_frame)
    print("---------------------------------")
    gif_output_path = create_gif_from_images(subject, images_paths_sorted, folder_path)  # nopep8
    print("---------------------------------")
    display_gif_with_gui(gif_output_path)


if __name__ == "__main__":
    main()
