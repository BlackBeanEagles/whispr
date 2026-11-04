# The Objects Have Questions

A comic case-file portfolio for Hridya Jain's Wispr Flow Hiring Challenge. Four everyday objects testify about how the project was made. The public studio lets visitors give an object a short story, a practical instruction, and a shareable QR case file.

**Live site:** https://case-files-jain.emergent.host/

## Challenge video

The [final 2:08 video](video/the-objects-have-questions-submission-final.mp4) uses animated Detective Mug panels, screenshots of the live site, and two clearly labeled stock reenactments. It explains the portfolio, why it was built, and how speaking the initial Emergent brief with Wispr Flow helped. Narration is generated; the video does not claim to show a live Wispr Flow recording.

The `video/` folder contains the editable script, scene data, screenshots, audio, and stock clips used to render the MP4. To rerender it locally on Windows:

```powershell
python -m pip install pillow opencv-python imageio-ffmpeg
python video/make_video.py
```

`make_voice_gtts.py` can regenerate the narration with `gTTS` and an internet connection. The rendered WAV files are included, so regenerating the voice is optional.

## Source status

The live web app is hosted in Emergent. Its source is currently available in that project’s code viewer, but a complete export was unavailable from the current account. This repository contains the video source and the live site link; it does not claim to contain a buildable copy of the web app.

## Footage credits

Stock reenactments are from Pexels: [vintage microphone by RDNE Stock project](https://www.pexels.com/video/a-vintage-microphone-8197868/) and [ceramic mug by cottonbro studio](https://www.pexels.com/video/coffee-hand-mug-desk-4065941/). See the [Pexels license](https://www.pexels.com/license/).
