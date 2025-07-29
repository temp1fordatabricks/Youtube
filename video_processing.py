import ffmpeg
import os

def extract_audio(video_path):
    try:
        audio_path = "temp_audio.aac"
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='copy')
            .run(cmd="ffmpeg", overwrite_output=True)
        )
        return audio_path
    except ffmpeg.Error as e:
        print(e.stderr)
        return None