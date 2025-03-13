import sys
import cv2
from PyQt6.QtWidgets import QApplication, QWidget , QPushButton,  QLineEdit, QLabel, QVBoxLayout, QFrame, QGridLayout, QFileDialog, QSpinBox
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIntValidator
from PyQt6.QtCore import Qt
from client import LaserClient 
from image import Line, scan_lines, ThreeViewsWindow


class LaserGUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # создаем окно
        self.setWindowTitle("Управление лазером")
        self.setGeometry(100, 100, 600, 700)
        
        #поле для рисования
        self.frame = QFrame(self)
        self.frame.setFixedSize(500,500)
        self.frame.setStyleSheet("background-color: white; border: 2px solid black;")
        
        self.canvas =QLabel(self.frame)
        self.canvas.setGeometry(0,0,500,500)
        
        self.pixmap = QPixmap(500,500)
        self.pixmap.fill(Qt.GlobalColor.white)
        self.canvas.setPixmap(self.pixmap)
        
        self.canvas.mousePressEvent = self.on_canvas_click
        self.path = {}
        self.laser_x = 250
        self.laser_y = 250
        self.radiation = True
        self.draw_laser()
        
        
        self.client = LaserClient()
        self.client.set_gui(self)
        
        #создаем кнопки
        self.move_button = QPushButton("Move Laser", self)
        self.move_button.clicked.connect(self.on_move_button_click)
        self.toggle_button = QPushButton("Radiation", self)
        self.toggle_button.clicked.connect(self.on_toggle_button_click)
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.on_reset_button_click)
        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.on_open_image)

        #поля ввода
        self.x_input = QLineEdit("250")
        self.x_input.setValidator(QIntValidator(0, 500, self))
        self.y_input = QLineEdit("250")
        self.y_input.setValidator(QIntValidator(0, 500, self))
        self.speed_input = QSpinBox(self)
        self.speed_input.setRange(1, 10)  # Скорость от 1 до 10
        self.speed_input.setValue(5)
        #подписи
        self.label_x = QLabel("X:")
        self.label_y = QLabel("Y:")
        self.label_speed = QLabel("Speed:")
        
        
        self.views_window = None
        #размещаем кнопку
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.label_x, 0, 0)
        grid_layout.addWidget(self.x_input, 0, 1)
        grid_layout.addWidget(self.label_y, 0, 2)
        grid_layout.addWidget(self.y_input, 0, 3)
        grid_layout.addWidget(self.label_speed, 0, 4)
        grid_layout.addWidget(self.speed_input, 0, 5)
        grid_layout.addWidget(self.move_button, 1,0,1,6)
        grid_layout.addWidget(self.toggle_button,2,0,1,6)
        grid_layout.addWidget(self.reset_button, 3, 0, 1, 6)
        grid_layout.addWidget(self.open_button, 4, 0, 1, 6)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)
        
    def on_open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.bmp)"
        )
        if not file_path:
            return

        # Загружаем gray
        img_o = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("Failed to load:", file_path)
            return

        # Threshold
        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        # Сканируем
        lines = scan_lines(thresh)

        # Создаём / открываем окно ThreeViewsWindow
        if self.views_window is None:
            self.views_window = ThreeViewsWindow()

        # Передаём данные
        self.views_window.update_views(img_o, thresh, lines)
        self.views_window.show()  
               
    def on_move_button_click(self):
        
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        speed = int(self.speed_input.value())
        self.client.send_move_command(x, y, speed)    
               
    def on_toggle_button_click(self):
        self.client.send_toggle_command()
    
    def on_reset_button_click(self):
        self.client.send_reset_command()
        self.x_input.setText("250")
        self.y_input.setText("250")      
    def on_canvas_click(self, event):
        
        click_x = event.position().x()
        click_y = event.position().y()
        
        x = int(click_x)
        y = int(click_y)
        
        self.x_input.setText(str(x))
        self.y_input.setText(str(y))
        
        speed = int(self.speed_input.text())
        
        self.client.send_move_command(x, y, speed)
        
        
        
          
      
    def draw_laser(self):
        self.pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(self.pixmap)
        step = 20
        painter.setPen(QColor(200,200,200))
        for x in range(0,500, step):
            painter.drawLine(x,0,x,500)
        for y in range(0,500, step):
            painter.drawLine(0,y,500,y)
        
        for mid, path_data in self.path.items():
            points = path_data["points"]
            radiation = path_data["radiation"]
            if len(points) < 2:
                continue
            if not radiation:
                continue
            painter.setPen(QColor(0,0,255))
            for i in range(1, len(points)):
                painter.drawLine(points[i-1][0], points[i-1][1],
                         points[i][0], points[i][1])
        
        if self.radiation:
            painter.setPen(QColor(255, 0, 0))
            painter.setBrush(QColor(255,0,0))
        else:
            painter.setPen(QColor(53, 100, 75))
            painter.setBrush(QColor(126,210,163))

        
        painter.drawEllipse(self.laser_x-3 , self.laser_y -3 , 6, 6) 
        
                       
        self.canvas.setPixmap(self.pixmap)
    def update_laser_position(self, x, y, radiation, move_id):
        self.radiation = radiation
        self.laser_x = x
        self.laser_y = y
        if move_id == 0:
            self.path.clear()
            self.laser_x = 250
            self.laser_y = 250
            self.radiation = True
            self.draw_laser()
            return
        if move_id not in self.path:
            self.path[move_id] = {
                "points": [],
                "radiation" : radiation  
            }
        if radiation:
            self.path[move_id]["points"].append((x,y))
        
        
        self.draw_laser()    
        
   
        
            
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LaserGUI()
    window.show()
    sys.exit(app.exec())