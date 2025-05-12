import moviepy.editor as mp

def extract_audio(video_path, audio_path):
    try:
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        clip.close()
        return audio_path
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")