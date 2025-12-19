from moviepy import ColorClip

def color_clip(size, duration, fps=25, color=(0, 0, 0), output='color.mp4'):
    clip = ColorClip(size=size, color=color, duration=duration)
    clip.write_videofile(output, fps=fps)


if __name__ == '__main__':
    size = (1920, 1080)
    duration = 5
    color_clip(size, duration, color=(255, 255, 255), output='color-1080p25.mp4')