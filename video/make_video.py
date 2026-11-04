from __future__ import annotations

import json
import math
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import imageio_ffmpeg
import cv2

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "video-assets"
SCENES = json.loads((ROOT / "video-scenes.json").read_text(encoding="utf-8"))["scenes"]
OUT = ROOT / "the-objects-have-questions-submission-final.mp4"
W, H, FPS = 1280, 720, 24
PAPER = "#f0e7d5"
INK = "#20180e"
RED = "#af382b"
MUTED = "#7d6d59"
FONT_SERIF = "C:/Windows/Fonts/georgiab.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"
SERIF = ImageFont.truetype(FONT_SERIF, 40)
MONO = ImageFont.truetype(FONT_MONO, 18)
CAPTION = ImageFont.truetype(FONT_MONO, 22)
QUOTE = ImageFont.truetype(FONT_SERIF, 42)
CARD = ImageFont.truetype(FONT_SERIF, 32)
STAMP = ImageFont.truetype(FONT_MONO, 21)
BUBBLE = ImageFont.truetype(FONT_MONO, 27)
CALLOUTS = {
    "THE OBJECTS HAVE QUESTIONS": "THE SUSPECT IS A PORTFOLIO.",
    "THE NOTEBOOK TESTIFIES": "IT WROTE DOWN EVERYTHING.",
    "THE MICROPHONE OBJECTS": "I WAS BORN FOR THIS ROLE!",
    "THE FIRST BRIEF WAS SPOKEN": "SHE SPOKE. THE SITE APPEARED.",
    "THE WORDS BECAME A LIVE SITE": "OBJECTION! IT ACTUALLY WORKED.",
    "NOW THE STUDIO IS OPEN": "YOUR DESK IS NEXT.",
    "A MUG FILES A COMPLAINT": "THREE MEETINGS. ONE COLD COFFEE.",
    "THE MUG HAS A STATEMENT": "PLEASE RINSE THE EVIDENCE.",
    "MEET THE OBJECT PASSPORT": "EVEN LOST THINGS HAVE A STORY.",
    "ASK THE OBJECT": "THE UMBRELLA HAS AN ALIBI.",
    "THE EVIDENCE IS LIVE": "CASE CLOSED? OPEN YOUR OWN.",
}


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if current and draw.textbbox((0, 0), trial, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def slide(scene: dict) -> Image.Image:
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)
    for yy in range(112, 600, 19):
        for xx in range(4 + (yy // 19 % 2) * 9, W, 19):
            draw.ellipse((xx, yy, xx + 3, yy + 3), fill="#dacbb3")
    draw.rectangle((0, 0, W, 102), fill=INK)
    draw.rectangle((0, 100, W, 105), fill=RED)
    draw.text((32, 14), scene["label"], font=MONO, fill="#d3b99c")
    draw.text((30, 43), scene["title"], font=SERIF, fill=PAPER)
    if scene.get("stock"):
        draw.rectangle((24, 118, 744, 583), fill=INK)
        draw.rectangle((30, 124, 738, 577), fill="#463b30")
        draw.text((44, 545), "DRAMATIC REENACTMENT / PEXELS", font=MONO, fill=PAPER, stroke_width=2, stroke_fill=INK)
    elif scene.get("image"):
        shot = Image.open(ASSETS / scene["image"]).convert("RGB")
        if "crop" in scene:
            shot = shot.crop(tuple(scene["crop"]))
        picture = ImageOps.fit(shot, (708, 453), Image.Resampling.LANCZOS, centering=(0.31, 0.5))
        draw.rectangle((24, 118, 744, 583), fill=INK)
        canvas.paste(picture, (30, 124))
        draw.rectangle((30, 542, 325, 577), fill=RED)
        draw.text((44, 548), "ACTUAL LIVE SITE", font=MONO, fill=PAPER)
    else:
        draw.rectangle((24, 118, 744, 583), fill=INK)
        draw.rectangle((30, 124, 738, 577), fill="#fff9eb")
        draw.text((49, 143), "SPOKEN INTO EMERGENT WITH WISPR FLOW", font=MONO, fill=RED)
        for i, line in enumerate(wrap(draw, "“" + scene["quote"] + "”", CARD, 620)):
            draw.text((54, 201 + i * 48), line, font=CARD, fill=INK)
    draw.rectangle((756, 118, 1254, 583), outline=RED, width=4)
    draw.text((777, 542), "DETECTIVE MUG / CASE NOTES", font=MONO, fill=RED)
    draw.rectangle((0, 605, W, H), fill=INK)
    draw.rectangle((0, 605, W, 609), fill=RED)
    for i, line in enumerate(wrap(draw, scene["narration"], CAPTION, 1210)):
        draw.text((34, 621 + i * 26), line, font=CAPTION, fill=PAPER)
    if scene["title"] == "THE EVIDENCE IS LIVE":
        draw.rectangle((30, 542, 738, 577), fill=RED)
        draw.text((39, 548), "case-files-jain.emergent.host", font=MONO, fill="#ffffff")
    return canvas


def add_stock_frame(frame: Image.Image, scene: dict, cap: cv2.VideoCapture, j: int) -> Image.Image:
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    source_frame = round(source_fps * (0.6 + j / FPS))
    cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame)
    ok, bgr = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, bgr = cap.read()
    if not ok:
        return frame
    shot = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    box = (30, 124, 738, 577)
    fitted = ImageOps.fit(shot, (box[2] - box[0], box[3] - box[1]), Image.Resampling.BILINEAR)
    if "mic" in scene["stock"]:
        fitted = fitted.filter(ImageFilter.GaussianBlur(14))
        portrait = ImageOps.contain(shot, (325, box[3] - box[1]), Image.Resampling.BILINEAR)
        fitted.paste(portrait, ((fitted.width - portrait.width) // 2, 0))
    frame.paste(fitted, box[:2])
    label = ImageDraw.Draw(frame)
    label.rectangle((box[0] + 10, box[3] - 39, box[0] + 382, box[3] - 8), fill=RED)
    label.text((box[0] + 20, box[3] - 35), "DRAMATIC REENACTMENT / PEXELS", font=MONO, fill=PAPER)
    return frame


def move_comic_panel(frame: Image.Image, scene: dict, j: int, frames: int) -> Image.Image:
    if scene.get("stock"):
        return frame
    box = (30, 124, 738, 542 if scene.get("image") else 577)
    panel = frame.crop(box)
    amount = j / max(frames - 1, 1)
    zoom = 1.0 + 0.055 * amount
    wide = round(panel.width * zoom)
    tall = round(panel.height * zoom)
    enlarged = panel.resize((wide, tall), Image.Resampling.BILINEAR)
    left = round((wide - panel.width) * (0.22 + 0.55 * amount))
    top = round((tall - panel.height) * (0.6 - 0.25 * amount))
    frame.paste(enlarged.crop((left, top, left + panel.width, top + panel.height)), box[:2])
    return frame


def add_stamps(frame: Image.Image, scene: dict, j: int, frames: int) -> Image.Image:
    # A fast rubber-stamp entrance and a restrained camera push on every exhibit.
    if j >= 7 and scene.get("image") and not scene.get("cartoon") and scene["title"] != "THE EVIDENCE IS LIVE":
        layer = Image.new("RGBA", (275, 62), (0, 0, 0, 0))
        mark = ImageDraw.Draw(layer)
        mark.rectangle((3, 3, 272, 59), outline=RED, width=4)
        mark.text((15, 19), "ENTERED INTO EVIDENCE", font=ImageFont.truetype(FONT_MONO, 15), fill=RED)
        layer = layer.rotate(-9, expand=True)
        frame.paste(layer, (400, 135), layer)
    return frame


def add_detective(frame: Image.Image, scene: dict, j: int) -> Image.Image:
    # A hand-drawn mug detective bobs, points at the real site, and lip-syncs in short beats.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    arrive = round(285 * max(0, 1 - j / 16))
    bob = round(7 * math.sin(j / 5))
    x, y = 974 + arrive, 352 + bob
    # Speech bubble grows into the frame; words enter one by one.
    if j >= 8:
        grow = min(1.0, (j - 7) / 8)
        left = round(780 + (1 - grow) * 180)
        top = round(139 + (1 - grow) * 65)
        right = round(1218 - (1 - grow) * 55)
        bottom = round(270 - (1 - grow) * 15)
        d.rounded_rectangle((left, top, right, bottom), radius=22, fill="#fffaf0", outline=INK, width=5)
        d.polygon([(1030, bottom - 3), (1060, bottom - 3), (1045, bottom + 25)], fill="#fffaf0")
        d.line([(1030, bottom - 3), (1045, bottom + 25), (1060, bottom - 3)], fill=INK, width=4)
        words = scene.get("bubble", CALLOUTS.get(scene["title"], "OPEN THE CASE.")).split()
        shown = max(1, min(len(words), round((j - 7) / 5)))
        phrase = " ".join(words[:shown])
        for k, line in enumerate(wrap(d, phrase, BUBBLE, 391)):
            d.text((left + 19, top + 21 + k * 32), line, font=BUBBLE, fill=INK)
    # Shoes and little detective legs.
    d.line([(x + 48, y + 172), (x + 36, y + 218)], fill=INK, width=9)
    d.line([(x + 132, y + 172), (x + 150, y + 218)], fill=INK, width=9)
    d.ellipse((x + 6, y + 207, x + 72, y + 227), fill=INK)
    d.ellipse((x + 119, y + 207, x + 188, y + 227), fill=INK)
    # Left hand points into the actual website panel.
    d.line([(x + 18, y + 95), (x - 98, y + 44), (x - 182, y + 50)], fill=INK, width=12, joint="curve")
    d.ellipse((x - 193, y + 34, x - 171, y + 59), fill="#fffaf0", outline=INK, width=4)
    d.line([(x + 164, y + 94), (x + 201, y + 122)], fill=INK, width=11)
    d.ellipse((x + 190, y + 113, x + 215, y + 138), fill="#fffaf0", outline=INK, width=4)
    # Mug body, handle, face, and an oversized detective hat.
    d.ellipse((x + 143, y + 63, x + 214, y + 153), fill="#d89a56", outline=INK, width=6)
    d.ellipse((x + 155, y + 79, x + 194, y + 132), fill=PAPER, outline=INK, width=4)
    d.rounded_rectangle((x, y + 45, x + 173, y + 177), radius=28, fill="#d89a56", outline=INK, width=7)
    d.ellipse((x + 13, y + 34, x + 164, y + 60), fill="#6a3b22", outline=INK, width=5)
    d.ellipse((x + 11, y + 37, x + 163, y + 56), fill="#f3d8aa")
    d.rounded_rectangle((x + 26, y - 5, x + 143, y + 39), radius=10, fill=INK)
    d.rectangle((x + 36, y + 9, x + 133, y + 23), fill=RED)
    d.rounded_rectangle((x - 4, y + 29, x + 174, y + 43), radius=7, fill=INK)
    blink = j % 52 in (20, 21, 22)
    if blink:
        d.line([(x + 43, y + 95), (x + 68, y + 95)], fill=INK, width=5)
        d.line([(x + 107, y + 95), (x + 132, y + 95)], fill=INK, width=5)
    else:
        d.ellipse((x + 42, y + 78, x + 69, y + 108), fill=PAPER, outline=INK, width=3)
        d.ellipse((x + 106, y + 78, x + 133, y + 108), fill=PAPER, outline=INK, width=3)
        d.ellipse((x + 49, y + 88, x + 60, y + 102), fill=INK)
        d.ellipse((x + 112, y + 88, x + 123, y + 102), fill=INK)
    if (j // 7) % 2 == 0:
        d.arc((x + 71, y + 112, x + 104, y + 144), 5, 175, fill=INK, width=5)
    else:
        d.ellipse((x + 77, y + 119, x + 98, y + 143), fill=INK)
    frame.paste(layer, (0, 0), layer)
    return frame


def combined_audio() -> list[float]:
    audio_out = ASSETS / "narration.wav"
    durations = []
    params = None
    with wave.open(str(audio_out), "wb") as out:
        for i, _ in enumerate(SCENES, 1):
            with wave.open(str(ASSETS / "audio" / f"{i:02}.wav"), "rb") as clip:
                if params is None:
                    params = clip.getparams()
                    out.setparams(params)
                else:
                    assert (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) == (
                        params.nchannels,
                        params.sampwidth,
                        params.framerate,
                    )
                frames = clip.readframes(clip.getnframes())
                out.writeframes(frames)
                speech_time = clip.getnframes() / clip.getframerate()
                pause = 0.7
                out.writeframes(b"\0" * round(pause * clip.getframerate() * clip.getnchannels() * clip.getsampwidth()))
                durations.append(speech_time + pause)
    return durations


def main() -> None:
    durations = combined_audio()
    total = sum(durations)
    slides = [slide(scene) for scene in SCENES]
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(ASSETS / "narration.wav"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", str(OUT),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert process.stdin
    elapsed = 0.0
    previous = slides[0]
    try:
        for i, (base, duration) in enumerate(zip(slides, durations)):
            frames = round(duration * FPS)
            scene = SCENES[i]
            cap = cv2.VideoCapture(str(ASSETS / scene["stock"])) if scene.get("stock") else None
            for j in range(frames):
                frame = base.copy()
                if cap is not None:
                    frame = add_stock_frame(frame, scene, cap, j)
                else:
                    frame = move_comic_panel(frame, scene, j, frames)
                frame = add_stamps(frame, scene, j, frames)
                frame = add_detective(frame, scene, j)
                if i and j < 15:
                    reveal = round((W + 160) * (j + 1) / 15) - 80
                    incoming = frame
                    frame = previous.copy()
                    mask = Image.new("L", (W, H), 0)
                    ImageDraw.Draw(mask).polygon(
                        [(0, 0), (reveal - 75, 0), (reveal + 75, H), (0, H)], fill=255
                    )
                    frame.paste(incoming, (0, 0), mask)
                    ImageDraw.Draw(frame).line(
                        [(reveal - 75, 0), (reveal + 75, H)], fill=RED, width=9
                    )
                progress = ImageDraw.Draw(frame)
                progress.rectangle((0, H - 5, round(W * (elapsed + j / FPS) / total), H), fill=RED)
                process.stdin.write(frame.tobytes())
            if cap is not None:
                cap.release()
            elapsed += duration
            previous = frame
    finally:
        process.stdin.close()
    error = process.stderr.read().decode("utf-8", errors="replace")
    if process.wait() != 0:
        raise RuntimeError(error[-4000:])
    print(f"Created {OUT} ({total:.1f} seconds)")


if __name__ == "__main__":
    main()
