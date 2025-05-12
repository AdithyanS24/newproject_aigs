from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import re

def concatenate_clips(highlight_dir):
    # Helper function to extract number from filename
    def extract_number(filename):
        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else -1

    # Get and sort video filenames by number
    video_filenames = sorted(
        [f for f in os.listdir(highlight_dir) if f.endswith(".mp4") and f.startswith("highlight_")],
        key=extract_number
    )

    # Load video clips in sorted order
    clips = []
    for filename in video_filenames:
        filepath = os.path.join(highlight_dir, filename)
        try:
            clip = VideoFileClip(filepath)
            clips.append(clip)
            print(f"✅ Loaded {filename} successfully.")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    # Concatenate and export final video
    if clips:
        final_clip = concatenate_videoclips(clips)
        final_video_path = os.path.join(highlight_dir, "final_highlights.mp4")
        final_clip.write_videofile(final_video_path, codec="libx264")
        for clip in clips:
            clip.close()
        final_clip.close()
        return final_video_path
    else:
        raise Exception("No clips were loaded. Cannot create final video.")