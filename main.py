from moviepy import (
    VideoClip,
    VideoFileClip,
    ImageSequenceClip,
    ImageClip,
    TextClip,
    ColorClip,
    AudioFileClip,
    AudioClip,
    CompositeVideoClip,
)

black = (0, 0, 0)

# Hintergrundvideo laden (3 Sekunden)
background = VideoFileClip("color-1080p25.mp4").subclipped(0, 3)

title = TextClip(
    text="Moin Meister",
    font="arial",
    font_size=80,
    color=black,
    size=(800, 200),
    method="caption",
    duration=3,
).with_position((1000, 100))

# Clips zusammensetzen
final_clip = CompositeVideoClip([background, title])

# Video als mp.4 exportieren
final_clip.write_videofile(
    "result.mp4",
    codec="libvpx-vp9",
    fps=24,
    preset="ultrafast",
    threads=4,
)