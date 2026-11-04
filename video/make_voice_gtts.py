from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / ".deps"))

from gtts import gTTS
import imageio_ffmpeg


root = Path(__file__).resolve().parent
scenes = json.loads((root / "video-scenes.json").read_text(encoding="utf-8"))["scenes"]
audio = root / "video-assets" / "audio"
audio.mkdir(exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

for i, scene in enumerate(scenes, 1):
    mp3 = audio / f"{i:02}.mp3"
    wav = audio / f"{i:02}.wav"
    gTTS(scene["narration"], lang="en", tld="co.in", slow=False).save(str(mp3))
    subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-i", str(mp3), "-af", "atempo=1.20", "-ar", "22050", "-ac", "1", str(wav)],
        check=True,
    )
    print(f"Narration {i}/{len(scenes)}", flush=True)
