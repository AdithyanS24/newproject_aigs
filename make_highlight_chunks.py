import librosa
import numpy as np
import pandas as pd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os

def generate_highlight_clips(video_path, audio_path, output_folder):
    print(f"DEBUG: Starting generate_highlight_clips")
    print(f"DEBUG: Video path: {video_path}")
    print(f"DEBUG: Audio path: {audio_path}")
    print(f"DEBUG: Output folder: {output_folder}")

    # Verify files exist
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load the audio file
    print(f"DEBUG: Loading audio with librosa")
    try:
        x, sr = librosa.load(audio_path, sr=16000)
    except Exception as e:
        raise Exception(f"Failed to load audio: {str(e)}")
    duration_seconds = librosa.get_duration(y=x, sr=sr)
    print(f"DEBUG: Audio Duration: {duration_seconds:.2f} seconds")

    # Parameters
    chunk_size = 10  # seconds per energy chunk
    window_length = chunk_size * sr
    highlight_chunk_duration = 10  # 10 seconds per highlight clip
    segments_per_block = 6  # 6 highlights per 10 min block
    block_duration = 600  # 10 minutes = 600 seconds

    # Calculate energy in 10s chunks
    print(f"DEBUG: Calculating energy chunks")
    energy = []
    start_times = []
    for i in range(0, len(x), window_length):
        chunk = x[i:i + window_length]
        if len(chunk) < 1:
            continue
        energy.append(np.sum(np.abs(chunk ** 2)))
        start_times.append(i // sr)

    if not energy:
        raise ValueError("No audio chunks generated. Audio may be too short or invalid.")

    df = pd.DataFrame({
        'energy': energy,
        'start': start_times,
        'end': [start + chunk_size for start in start_times]
    })
    print(f"DEBUG: DataFrame created with {len(df)} chunks")

    # Break into 10-min blocks and select top 6 high-energy 10s clips in each
    highlight_clips = []
    num_blocks = int(duration_seconds // block_duration)
    print(f"DEBUG: Processing {num_blocks} 10-minute blocks")

    for block_idx in range(num_blocks):
        block_start = block_idx * block_duration
        block_end = block_start + block_duration

        # Filter chunks within the current 10-minute block
        block_df = df[(df['start'] >= block_start) & (df['end'] <= block_end)]
        print(f"DEBUG: Block {block_idx} has {len(block_df)} chunks")

        if block_df.empty:
            print(f"DEBUG: Skipping empty block {block_idx}")
            continue

        # Sort by energy and pick top 6
        top_clips = block_df.sort_values(by='energy', ascending=False).head(segments_per_block)
        print(f"DEBUG: Selected {len(top_clips)} top clips in block {block_idx}")

        for _, row in top_clips.iterrows():
            highlight_clips.append((int(row['start']), int(row['end'])))

    if not highlight_clips:
        raise ValueError("No highlight clips generated. Audio may be too short or lack high-energy segments.")

    # Output the highlight video clips
    highlight_paths = []
    print(f"DEBUG: Generating {len(highlight_clips)} highlight clips")
    for i, (start, end) in enumerate(highlight_clips):
        output_name = f"{output_folder}/highlight_{i + 1}.mp4"
        try:
            print(f"DEBUG: Creating highlight {i + 1} from {start}s to {end}s")
            ffmpeg_extract_subclip(video_path, start, end, targetname=output_name)
            highlight_paths.append(output_name)
            print(f"✅ Highlight video {i + 1} created: {output_name}")
        except Exception as e:
            print(f"❌ Error creating highlight video {i + 1}: {e}")

    if not highlight_paths:
        raise Exception("No highlight clips were created.")

    print(f"DEBUG: Returning {len(highlight_paths)} highlight paths")
    return highlight_paths