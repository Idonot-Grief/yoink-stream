import subprocess
import os
import threading

STREAM_KEY_FILE = "./streamkey.txt"
VIDEO_PATH = "./assets/video.mp4"

def input_with_timeout(prompt, timeout=5):
    """Wait for user input for a given timeout. Return None if timeout expires."""
    user_input = [None]

    def get_input():
        user_input[0] = input(prompt)

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    return user_input[0]

def get_stream_key():
    saved_key = None
    if os.path.isfile(STREAM_KEY_FILE):
        with open(STREAM_KEY_FILE, "r") as f:
            saved_key = f.read().strip()

    if saved_key:
        user_input = input_with_timeout(
            f"Press Enter to use saved stream key or type a new one (auto-uses saved in 5s): ", 5
        )
        if not user_input:  # Timeout or empty input
            print("Using saved stream key.")
            return saved_key
        else:
            stream_key = user_input.strip()
    else:
        stream_key = input("Enter your YouTube stream key: ").strip()

    # Save the stream key
    with open(STREAM_KEY_FILE, "w") as f:
        f.write(stream_key)
    print(f"Stream key saved to {STREAM_KEY_FILE}")
    return stream_key

def start_stream(stream_key, video_path=VIDEO_PATH):
    if not os.path.isfile(video_path):
        print(f"Error: Video file '{video_path}' not found!")
        return

    youtube_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", video_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "3000k",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-vf", "scale=1280:720",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        youtube_url
    ]

    print("Starting live stream... Press Ctrl+C to stop.")
    try:
        subprocess.run(ffmpeg_command)
    except KeyboardInterrupt:
        print("\nStream stopped by user.")

if __name__ == "__main__":
    key = get_stream_key()
    start_stream(key)
