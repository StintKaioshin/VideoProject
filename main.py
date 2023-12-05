import os
import random
from moviepy.editor import VideoFileClip, clips_array, CompositeAudioClip
import time
import schedule
from youtube_uploader import upload_video_to_youtube
import argparse

def get_random_video(directory):
    videos = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.mp4', '.mov', '.avi'))]
    chosen_video = random.choice(videos) if videos else None
    return chosen_video

def combine_videos(video1_path, video2_path, output_path):
    clip1 = VideoFileClip(video1_path)
    clip2 = VideoFileClip(video2_path).volumex(0.15)
    target_width = 1080
    target_height_half = 1920 // 2  
    clip1_resized = clip1.resize(height=target_height_half).crop(x_center=clip1.w / 2, width=target_width, height=target_height_half)
    clip2_resized = clip2.resize(height=target_height_half).crop(x_center=clip2.w / 2, width=target_width, height=target_height_half)
    duration = min(clip1_resized.duration, clip2_resized.duration)
    clip1_resized = clip1_resized.set_duration(duration)
    clip2_resized = clip2_resized.set_duration(duration)
    final_clip = clips_array([[clip1_resized], [clip2_resized]])
    audio1 = clip1_resized.audio
    audio2 = clip2_resized.audio.volumex(0.15)
    final_audio = CompositeAudioClip([audio1, audio2])
    final_clip.audio = final_audio.set_duration(duration)
    final_clip.write_videofile(output_path, codec="libx264", fps=24)
    print(f"Video saved to {output_path}")

def get_random_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            titles = [line.strip() for line in file if line.strip()]
            return random.choice(titles) if titles else "Default Title"
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return "Default Title"
    

    
def job():
    video1 = get_random_video('C:/Users/aiden/OneDrive/Desktop/VideoProject/folder1')
    video2 = get_random_video('C:/Users/aiden/OneDrive/Desktop/VideoProject/folder2')
    if video1 and video2:
        combined_video_path = 'C:\\Users\\aiden\\OneDrive\\Desktop\\VideoProject\\outputvids\\output.mp4'
        combine_videos(video1, video2, combined_video_path)

        random_title = get_random_title('C:/Users/aiden/OneDrive/Desktop/VideoProject/titleopts.txt')

        upload_video_to_youtube(
            video_path=combined_video_path,
            title=random_title,
            description="Subscribe NOW",
            category="22",  # Choose the appropriate category
            keywords="Tate, AdinRoss",
            privacy_status="public"  # or "private", "unlisted"
        )

# schedule.every().day.at("10:00").do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(60)

job()
