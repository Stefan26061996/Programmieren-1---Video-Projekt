import cv2

class PositionSelector:
    def __init__(self, frame, text="Moin Meister"):
        self.frame = frame.copy()
        self.text = text
        self.pos = [100, 100]
        self.scale = 2.0  # Startgröße
        self.dragging = False

    def mouse_event(self, event, x, y, flags, param):
        # Dragging
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.offset_x = x - self.pos[0]
            self.offset_y = y - self.pos[1]

        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.pos[0] = x - self.offset_x
            self.pos[1] = y - self.offset_y

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

        # Mausrad → Größe ändern
        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.scale += 0.1
            else:
                self.scale -= 0.1
            self.scale = max(0.3, min(self.scale, 10))  # Grenzen setzen

    def select(self):
        cv2.namedWindow("Position auswählen")
        cv2.setMouseCallback("Position auswählen", self.mouse_event)

        while True:
            preview = self.frame.copy()

            cv2.putText(
                preview,
                self.text,
                tuple(self.pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.scale,
                (0, 0, 0),
                4,
                cv2.LINE_AA
            )

            cv2.imshow("Position auswählen", preview)

            key = cv2.waitKey(16)

            if key == 27:  # ESC = bestätigen
                break

        cv2.destroyAllWindows()
        return tuple(self.pos), self.scale
