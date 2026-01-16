from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip
import cv2
import numpy as np
import os
from typing import Tuple, Optional
from PIL import ImageFont


class FontManager:
    """Verwaltet Fonts und findet verfügbare"""

    @staticmethod
    def get_safe_font():
        """Gibt einen sicheren Font zurück"""
        # Liste von Fonts in Reihenfolge der Priorität
        font_priority = [
            "Arial",  # Windows/Mac
            "Helvetica",  # Mac
            "DejaVu-Sans",  # Linux
            "Liberation-Sans",  # Linux
            "Verdana",  # Windows/Mac
            "Times-New-Roman",  # Überall
            None  # System-Standard
        ]

        for font in font_priority:
            if font is None:
                return None

            try:
                # Teste ob Font existiert
                ImageFont.truetype(font, 10)
                print(f"✅ Gefundener Font: {font}")
                return font
            except:
                continue

        return None  # Kein spezieller Font


class PositionSelector:
    def __init__(self, frame: np.ndarray, text: str = "HAW Hamburg"):
        self.frame = frame.copy()
        self.text = text
        self.pos = [100, 100]
        self.scale = 1.0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def mouse_event(self, event: int, x: int, y: int, flags: int, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            text_size = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_SIMPLEX, self.scale, 3)[0]
            text_rect = (self.pos[0], self.pos[1] - text_size[1],
                         self.pos[0] + text_size[0], self.pos[1])

            if text_rect[0] <= x <= text_rect[2] and text_rect[1] <= y <= text_rect[3]:
                self.dragging = True
                self.offset_x = x - self.pos[0]
                self.offset_y = y - self.pos[1]

        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.pos[0] = x - self.offset_x
            self.pos[1] = y - self.offset_y

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.scale += 0.1
            else:
                self.scale -= 0.1
            self.scale = max(0.3, min(self.scale, 5.0))

    def select(self) -> Tuple[Tuple[int, int], float]:
        print("\n🎯 INTERAKTIVE POSITIONSWAHL")
        print("-" * 40)
        print("• Ziehen Sie den Text mit der Maus")
        print("• Mausrad: Größe ändern")
        print("• ESC-Taste: Bestätigen")
        print("-" * 40)

        cv2.namedWindow("Position auswählen - ESC zum Bestätigen")
        cv2.setMouseCallback("Position auswählen - ESC zum Bestätigen", self.mouse_event)

        while True:
            preview = self.frame.copy()

            # Schatten
            cv2.putText(
                preview,
                self.text,
                (self.pos[0] + 2, self.pos[1] + 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.scale,
                (0, 0, 0),
                3,
                cv2.LINE_AA
            )
            # Haupttext
            cv2.putText(
                preview,
                self.text,
                tuple(self.pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.scale,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            # Info
            h, w = preview.shape[:2]
            cv2.line(preview, (0, self.pos[1]), (w, self.pos[1]), (0, 255, 0), 1)
            cv2.line(preview, (self.pos[0], 0), (self.pos[0], h), (0, 255, 0), 1)

            info = f"Position: ({self.pos[0]}, {self.pos[1]}) | Größe: {self.scale:.1f}"
            cv2.putText(preview, info, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Position auswählen - ESC zum Bestätigen", preview)

            key = cv2.waitKey(16) & 0xFF
            if key == 27:
                break

        cv2.destroyAllWindows()
        return tuple(self.pos), self.scale


class FileScanner:
    @staticmethod
    def scan() -> list:
        media_files = []
        for f in os.listdir("."):
            f_lower = f.lower()
            if f_lower.endswith((".mp4", ".mov", ".webm", ".avi")) or \
                    f_lower.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                media_files.append(f)
        return media_files

    @staticmethod
    def choose(files: list) -> str:
        if not files:
            raise FileNotFoundError("Keine Dateien gefunden!")

        print("\n📁 Verfügbare Dateien:")
        for i, f in enumerate(files):
            print(f"  [{i}] {f}")

        while True:
            try:
                choice = int(input("\nDatei auswählen (Nummer): "))
                if 0 <= choice < len(files):
                    return files[choice]
                print(f"❌ Bitte Zahl zwischen 0 und {len(files) - 1} eingeben!")
            except ValueError:
                print("❌ Ungültige Eingabe! Bitte Zahl eingeben.")


class UserInput:
    @staticmethod
    def ask_opacity() -> float:
        while True:
            try:
                value = int(input("Transparenz (0-100%): "))
                if 0 <= value <= 100:
                    return value / 100
                print("❌ Bitte Zahl zwischen 0 und 100!")
            except ValueError:
                print("❌ Bitte gültige Zahl eingeben!")

    @staticmethod
    def ask_text() -> str:
        text = input("Wasserzeichen-Text (Enter für 'HAW Hamburg'): ").strip()
        return text if text else "HAW Hamburg"

    @staticmethod
    def ask_logo() -> Optional[str]:
        print("\n📎 Optional: Logo als Wasserzeichen verwenden")
        logo_files = [f for f in os.listdir(".")
                      if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        if not logo_files:
            print("⚠️  Keine Bilddateien für Logo gefunden")
            return None

        print("Verfügbare Logos:")
        for i, f in enumerate(logo_files):
            print(f"  [{i}] {f}")
        print(f"  [{len(logo_files)}] Kein Logo verwenden")

        while True:
            try:
                choice = int(input(f"Logo wählen (0-{len(logo_files)}): "))
                if 0 <= choice < len(logo_files):
                    return logo_files[choice]
                elif choice == len(logo_files):
                    return None
                print(f"❌ Bitte Zahl zwischen 0 und {len(logo_files)}!")
            except ValueError:
                print("❌ Bitte gültige Zahl eingeben!")


class MediaLoader:
    @staticmethod
    def load(filename: str):
        if filename.lower().endswith((".mp4", ".mov", ".webm", ".avi")):
            clip = VideoFileClip(filename)
            first_frame = clip.get_frame(0)
            return "video", clip, first_frame
        elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            clip = ImageClip(filename)
            first_frame = clip.get_frame(0)
            return "image", clip, first_frame
        else:
            raise ValueError(f"Nicht unterstütztes Format: {filename}")


class WatermarkCreator:
    def __init__(self, text: str, opacity: float,
                 position: Tuple[int, int], scale: float,
                 bg_color: str = "rgba(0,0,0,0.5)"):
        self.text = text
        self.opacity = opacity
        self.position = position
        self.scale = scale
        self.bg_color = bg_color
        self.font_name = FontManager.get_safe_font()  # Sicherer Font

    def calculate_font_size(self) -> int:
        return int(40 * self.scale)

    def calculate_size(self) -> Tuple[int, int]:
        width = int(400 * self.scale)
        height = int(100 * self.scale)
        return (width, height)

    def create_text(self):
        """Erstellt Text-Wasserzeichen mit sicherem Font"""
        font_size = self.calculate_font_size()
        size = self.calculate_size()

        try:
            # Versuch 1: Mit Font
            if self.font_name:
                text_clip = TextClip(
                    text=self.text,
                    font=self.font_name,
                    font_size=font_size,
                    color="white",
                    size=size,
                    method="caption",
                    bg_color=self.bg_color,
                    stroke_color="black",
                    stroke_width=1
                )
            else:
                # Versuch 2: Ohne Font (MoviePy Standard)
                text_clip = TextClip(
                    text=self.text,
                    font_size=font_size,
                    color="white",
                    size=size,
                    method="caption",
                    bg_color=self.bg_color
                )

            return text_clip.with_opacity(self.opacity).with_position(self.position)

        except Exception as e:
            print(f"⚠️  Font-Fehler, verwende einfache Version: {e}")
            # Fallback: Einfaches TextClip
            return TextClip(
                txt=self.text,
                fontsize=font_size,
                color='white'
            ).with_opacity(self.opacity).with_position(self.position).with_duration(1)

    def create_logo(self, logo_path: str):
        if not logo_path or not os.path.exists(logo_path):
            return None

        try:
            logo_position = (self.position[0] + self.calculate_size()[0] + 10,
                             self.position[1])

            logo = (
                ImageClip(logo_path)
                .with_opacity(self.opacity)
                .resize(self.scale)
                .with_position(logo_position)
            )
            return logo
        except Exception as e:
            print(f"⚠️  Logo konnte nicht geladen werden: {e}")
            return None


class Exporter:
    @staticmethod
    def export(background, watermark_clips, output_name: str, media_type: str):
        if media_type == "video":
            for clip in watermark_clips:
                clip = clip.with_duration(background.duration)

            final = CompositeVideoClip([background] + watermark_clips)

            # Einfache Export-Einstellungen
            try:
                final.write_videofile(
                    f"{output_name}.mp4",
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None
                )
            except Exception as e:
                print(f"⚠️  Video-Export-Fehler: {e}")
                print("Versuche alternative Einstellungen...")
                final.write_videofile(
                    f"{output_name}.mp4",
                    fps=24
                )
        else:
            final = CompositeVideoClip([background] + watermark_clips)
            final.save_frame(f"{output_name}.png")
            print(f"📸 Bild gespeichert als: {output_name}.png")


def main():
    print("\n" + "=" * 60)
    print("🎬 VIDEO PROJEKT - WASSERZEICHEN TOOL")
    print("=" * 60)

    try:
        # Font-Info
        print("🔤 Suche nach verfügbaren Fonts...")
        font = FontManager.get_safe_font()
        if font:
            print(f"✅ Verwende Font: {font}")

        # 1. Datei auswählen
        files = FileScanner.scan()
        selected_file = FileScanner.choose(files)
        print(f"✅ Ausgewählt: {selected_file}")

        # 2. Medien laden
        media_type, background, first_frame = MediaLoader.load(selected_file)
        print(f"📊 Typ: {'Video' if media_type == 'video' else 'Bild'}")
        print(f"📏 Größe: {background.size}")

        # 3. Einstellungen
        print("\n⚙️  Wasserzeichen-Einstellungen:")
        text = UserInput.ask_text()
        opacity = UserInput.ask_opacity()
        logo_path = UserInput.ask_logo()

        # 4. Interaktive Position
        print("\n" + "=" * 60)
        print("🖱️  INTERAKTIVE POSITIONS- UND GRÖSSENAUSWAHL")
        print("=" * 60)

        frame_for_cv = cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR)
        position_selector = PositionSelector(frame_for_cv, text)
        position, scale = position_selector.select()

        print(f"\n✅ Position ausgewählt: {position}")
        print(f"✅ Größe: {scale:.1f}x")

        # 5. Wasserzeichen erstellen
        creator = WatermarkCreator(text, opacity, position, scale)

        watermark_clips = [creator.create_text()]
        if logo_path:
            logo_clip = creator.create_logo(logo_path)
            if logo_clip:
                watermark_clips.append(logo_clip)
                print(f"✅ Logo hinzugefügt: {logo_path}")

        # 6. Export
        output_name = f"{os.path.splitext(selected_file)[0]}_wasserzeichen"

        print(f"\n💾 Exportiere als: {output_name}...")
        Exporter.export(background, watermark_clips, output_name, media_type)

        print("✅ Fertig! Ergebnis wurde gespeichert.")

        # Cleanup
        if media_type == "video":
            background.close()
            for clip in watermark_clips:
                clip.close()

        # Ergebnis anzeigen
        if media_type == "image" and os.path.exists(f"{output_name}.png"):
            result = cv2.imread(f"{output_name}.png")
            if result is not None:
                cv2.imshow("Ergebnis", result)
                print("🎯 Drücke eine Taste um das Fenster zu schließen...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("\n\n⚠️  Programm durch Benutzer abgebrochen")
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    # Installation prüfen
    try:
        import cv2
        from moviepy import VideoFileClip
        from PIL import ImageFont

        # Teste Fonts
        try:
            ImageFont.truetype("Arial", 10)
            print("✅ Font 'Arial' verfügbar")
        except:
            print("⚠️  Font 'Arial' nicht verfügbar")

        main()
    except ImportError as e:
        print(f"❌ Fehlende Abhängigkeit: {e}")
        print("\n📦 Bitte installieren mit:")
        print("   pip install opencv-python moviepy numpy pillow")