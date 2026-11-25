#!/usr/bin/env python3
"""Download a video/audio URL with yt-dlp and merge streams with ffmpeg.

Standalone CLI used by the "video-downloader" Kiro skill (and runnable by hand).
It mirrors the extension's native host behaviour:
  - resolves ffmpeg automatically (PATH, then common user-local locations),
  - merges separate video+audio into a single mp4,
  - keeps readable non-ASCII titles (e.g. Chinese) while sanitising for the OS,
  - defaults the output folder to the current user's Downloads directory.

Examples:
  python download_media.py "https://www.bilibili.com/video/BV1ke5U65ECa"
  python download_media.py URL --quality 1080
  python download_media.py URL --audio
  python download_media.py URL --output "D:/clips"
"""
import argparse
import os
import shutil
import subprocess
import sys


# Maps the friendly quality names to yt-dlp -f format expressions.
QUALITY_FORMATS = {
    "best": "bestvideo*+bestaudio/best",
    "2160": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
    "1440": "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "360": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "audio": "bestaudio/best",
}


def find_ffmpeg_dir():
    """Return a directory containing ffmpeg.exe/ffmpeg, or None."""
    exe = shutil.which("ffmpeg")
    if exe:
        return os.path.dirname(exe)

    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "ffmpeg", "bin"),
        os.path.join(home, "ffmpeg", "ffmpeg", "bin"),
        os.path.join("C:\\", "ffmpeg", "bin"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Links"),
        "/usr/bin",
        "/usr/local/bin",
        "/opt/homebrew/bin",
    ]
    for d in candidates:
        name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        if d and os.path.isfile(os.path.join(d, name)):
            return d
    return None


def default_download_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def check_tools():
    """Return (ok, message). ok is False when yt-dlp is missing."""
    if shutil.which("yt-dlp") is None:
        return False, "yt-dlp not found on PATH. Install it (e.g. pip install yt-dlp)."
    return True, ""


def build_command(url, quality, output_dir, ffmpeg_dir):
    fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["best"])
    is_audio_only = quality == "audio"

    out_template = os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s")

    cmd = ["yt-dlp", "-f", fmt, "-o", out_template]
    if not is_audio_only:
        cmd += ["--merge-output-format", "mp4"]
    if ffmpeg_dir:
        cmd += ["--ffmpeg-location", ffmpeg_dir]
    # --windows-filenames keeps non-ASCII titles while removing illegal chars.
    cmd += ["--no-playlist", "--windows-filenames", url]
    return cmd, is_audio_only


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Download a video/audio URL with yt-dlp, merging to a single file."
    )
    parser.add_argument("url", help="The media page URL to download.")
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        choices=list(QUALITY_FORMATS.keys()),
        help="Target quality (default: best). Use 'audio' for audio-only.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory (default: the current user's Downloads folder).",
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Shortcut for --quality audio (audio only).",
    )
    args = parser.parse_args(argv)

    quality = "audio" if args.audio else args.quality

    ok, msg = check_tools()
    if not ok:
        print("ERROR: " + msg, file=sys.stderr)
        return 2

    output_dir = args.output or default_download_dir()
    output_dir = os.path.abspath(os.path.expanduser(output_dir))
    os.makedirs(output_dir, exist_ok=True)

    ffmpeg_dir = find_ffmpeg_dir()
    needs_merge = quality != "audio"
    if needs_merge and not ffmpeg_dir:
        print(
            "ERROR: ffmpeg not found, so video and audio cannot be merged.\n"
            "       Install ffmpeg, or use --audio for audio-only.",
            file=sys.stderr,
        )
        return 3

    cmd, is_audio_only = build_command(args.url, quality, output_dir, ffmpeg_dir)

    print("Downloading to: %s" % output_dir)
    print("Quality: %s%s" % (quality, " (audio only)" if is_audio_only else ""))
    print("ffmpeg: %s" % (ffmpeg_dir or "not found"))
    print("-" * 60)

    # Stream yt-dlp output live so the user sees progress.
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        print("ERROR: could not launch yt-dlp.", file=sys.stderr)
        return 2

    if result.returncode == 0:
        print("-" * 60)
        print("Done. Saved to: %s" % output_dir)
        return 0

    print("-" * 60)
    print("Download failed (yt-dlp exit code %d)." % result.returncode, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
