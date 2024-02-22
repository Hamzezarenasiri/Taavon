import subprocess


def video_to_gif(video_input_path: str, img_output_path: str):
    subprocess.call(
        [
            "ffmpeg",
            "-i",
            video_input_path,
            "-t",
            "5",
            "-r",
            "15",
            "-vf",
            "fps=10,scale = 320:-1",
            "-loop",
            "0",
            img_output_path,
        ]
    )
