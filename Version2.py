from moviepy import (
    VideoFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
)
import os


SUPPORTED_VIDEOS = (".mp4", ".mov", ".webm")
SUPPORTED_IMAGES = (".png", ".jpg", ".jpeg")


class FileScanner:
    @staticmethod
    def scan():
        media_files = [
            f for f in os.listdir(".")
            if f.lower().endswith(SUPPORTED_VIDEOS + SUPPORTED_IMAGES)
        ]
        if not media_files:
            raise FileNotFoundError("Keine Bild- oder Videodateien im Projektordner gefunden.")
        return media_files

    @staticmethod
    def choose(files):
        print("\nGefundene Dateien:")
        for index, filename in enumerate(files):
            print(f"[{index}] {filename}")

        while True:
            try:
                choice = int(input("Datei auswählen (Nummer): "))
                return files[choice]
            except (ValueError, IndexError):
                print("Ungültige Auswahl. Bitte erneut versuchen.")


class UserInput:
    @staticmethod
    def ask_opacity():
        while True:
            try:
                value = int(input("Text-Transparenz in Prozent (0–100): "))
                if 0 <= value <= 100:
                    return value / 100
            except ValueError:
                pass
            print("Bitte eine Zahl zwischen 0 und 100 eingeben.")


class MediaLoader:
    @staticmethod
    def load(filename):
        if filename.lower().endswith(SUPPORTED_VIDEOS):
            clip = VideoFileClip(filename).subclipped(0, 3)
            return "video", clip

        if filename.lower().endswith(SUPPORTED_IMAGES):
            clip = ImageClip(filename)
            return "image", clip

        raise ValueError("Nicht unterstütztes Dateiformat.")


class TextOverlay:
    def __init__(self, text, opacity):
        self.text = text
        self.opacity = opacity

    def create(self):
        return (
            TextClip(
                text=self.text,
                font="arial",
                font_size=80,
                color="black",
                size=(800, 200),
                method="caption",
            )
            .with_opacity(self.opacity)
            .with_position((1000, 100))
        )


class Exporter:
    @staticmethod
    def export_video(background, text_clip, output_name):
        text_clip = text_clip.with_duration(background.duration)
        final_clip = CompositeVideoClip([background, text_clip])

        final_clip.write_videofile(
            f"{output_name}.mp4",
            codec="libvpx-vp9",
            fps=24,
            preset="ultrafast",
            threads=4,
        )

    @staticmethod
    def export_image(background, text_clip, output_name):
        frame = CompositeVideoClip([background, text_clip]).get_frame(0)
        ImageClip(frame).save_frame(f"{output_name}.jpg")


def main():
    try:
        files = FileScanner.scan()
        selected_file = FileScanner.choose(files)

        opacity = UserInput.ask_opacity()
        media_type, background = MediaLoader.load(selected_file)

        text_overlay = TextOverlay("Moin Meister", opacity).create()
        output_name = os.path.splitext(selected_file)[0] + "_result"

        if media_type == "video":
            Exporter.export_video(background, text_overlay, output_name)
        else:
            Exporter.export_image(background, text_overlay, output_name)

        print("Export abgeschlossen.")

    except Exception as error:
        print(f"Fehler: {error}")


if __name__ == "__main__":
    main()