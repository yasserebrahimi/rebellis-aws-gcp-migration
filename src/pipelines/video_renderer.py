import subprocess, shlex

def render_mp4(frames_dir: str, out_path: str, fps: int = 30):
    """
    Render frames as MP4 using ffmpeg.
    """
    cmd = f'ffmpeg -y -framerate {fps} -i {frames_dir}/%06d.png -c:v libx264 -pix_fmt yuv420p {shlex.quote(out_path)}'
    subprocess.check_call(cmd, shell=True)
    return out_path
