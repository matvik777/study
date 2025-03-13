import cv2
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap, QImage, QColor
from PyQt6.QtCore import Qt

class Line:
    """Хранит одну горизонтальную линию: начало (x,y) и длину ex."""
    def __init__(self, sx, sy):
        self.x = sx
        self.y = sy
        self.ex = 0

def scan_lines(thresh_img):
    """
    Сканируем пороговое изображение (0 или 255) построчно.
    Ищем участки, где пиксели == 255 (белые).
    Возвращаем список объектов Line(x, y, ex).
    """
    lines = []
    height, width = thresh_img.shape

    for y in range(height):
        has_line = False
        current_line = None
        for x in range(width):
            if thresh_img[y, x] == 255:
                if has_line:
                    current_line.ex += 1
                else:
                    current_line = Line(x, y)
                    current_line.ex = 1
                    has_line = True
            else:
                if has_line:
                    lines.append(current_line)
                    has_line = False
                    current_line = None
        # если строка закончилась, а линия тянулась
        if has_line and current_line is not None:
            lines.append(current_line)

    return lines

def cv2_to_pixmap(cv2_img):
    """Переводим numpy-массив (grayscale/1ch или color/3ch) в QPixmap (RGB888)."""
    if len(cv2_img.shape) == 2:
        rgb = cv2.cvtColor(cv2_img, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg)

class ThreeViewsWindow(QMainWindow):
    """
    Окно, показывающее три изображения:
    - Исходное grayscale
    - Пороговое
    - Результат (линии)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Three Views")
        self.setGeometry(150, 150, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Три QLabel
        self.orig_label = QLabel("Original")
        self.orig_label.setStyleSheet("background-color: gray;")
        self.orig_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.thresh_label = QLabel("Threshold")
        self.thresh_label.setStyleSheet("background-color: gray;")
        self.thresh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lines_label = QLabel("Lines")
        self.lines_label.setStyleSheet("background-color: gray;")
        self.lines_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.orig_label)
        layout.addWidget(self.thresh_label)
        layout.addWidget(self.lines_label)

    def update_views(self, orig_img, thresh_img, lines):
        """
        Принимает: orig_img (numpy gray), 
                   thresh_img (numpy binary),
                   lines (список Line).
        Переводит orig и thresh в QPixmap,
        рисует lines -> QPixmap,
        вставляет в три лейбла.
        """
        # 1) Исходное
        pix_orig = cv2_to_pixmap(orig_img)
        self.orig_label.setPixmap(
            pix_orig.scaled(self.orig_label.width(),
                            self.orig_label.height(),
                            Qt.AspectRatioMode.KeepAspectRatio)
        )

        # 2) Threshold
        pix_thresh = cv2_to_pixmap(thresh_img)
        self.thresh_label.setPixmap(
            pix_thresh.scaled(self.thresh_label.width(),
                              self.thresh_label.height(),
                              Qt.AspectRatioMode.KeepAspectRatio)
        )

        # 3) Lines
        h, w = thresh_img.shape
        pix_lines = self.draw_lines_on_black(lines, w, h)
        self.lines_label.setPixmap(
            pix_lines.scaled(self.lines_label.width(),
                             self.lines_label.height(),
                             Qt.AspectRatioMode.KeepAspectRatio)
        )

    def draw_lines_on_black(self, lines, width, height):
        """
        Рисует белые линии на чёрном QImage(width x height),
        возвращает QPixmap.
        """
        qimg = QImage(width, height, QImage.Format.Format_RGB888)
        qimg.fill(Qt.GlobalColor.black)

        color = QColor(255, 255, 255)
        for ln in lines:
            x_start = ln.x
            x_end   = ln.x + ln.ex
            y       = ln.y

            if y < 0 or y >= height:
                continue
            if x_start < 0:
                x_start = 0
            if x_end > width:
                x_end = width

            for x in range(x_start, x_end):
                qimg.setPixel(x, y, color.rgb())

        return QPixmap.fromImage(qimg)
