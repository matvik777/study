import sys
from PyQt6.QtWidgets import QApplication, QWidget , QPushButton,  QLineEdit, QLabel, QVBoxLayout, QFrame, QGridLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from client import LaserClient 
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
        self.trail = []
        self.laser_x = 250
        self.laser_y = 250
        self.radiation = True
        self.draw_laser()
        
        
        self.client = LaserClient()
        self.client.set_gui(self)
        
                
        #создаем кнопки
        self.move_button = QPushButton("Move Laser", self)
        self.move_button.clicked.connect(self.on_button_click)
        
        #поля ввода
        self.x_input = QLineEdit("400")
        self.y_input = QLineEdit("400")
        self.speed_input = QLineEdit("5")
        
        #подписи
        self.label_x = QLabel("X:")
        self.label_y = QLabel("Y:")
        self.label_speed = QLabel("Speed:")
        
        
        
        #размещаем кнопку
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.label_x, 0, 0)
        grid_layout.addWidget(self.x_input, 0, 1)
        grid_layout.addWidget(self.label_y, 0, 2)
        grid_layout.addWidget(self.y_input, 0, 3)
        grid_layout.addWidget(self.label_speed, 0, 4)
        grid_layout.addWidget(self.speed_input, 0, 5)
        grid_layout.addWidget(self.move_button, 1,0,1,6)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout
                       )     
    def on_button_click(self):
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        speed = int(self.speed_input.text())
        self.client.send_move_command(x, y, speed)       
    
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
        if len(self.trail) > 1 and self.radiation:
            painter.setPen(QColor(0,0,255))
            for i in range(1, len(self.trail)):
                painter.drawLine(self.trail[i-1][0], self.trail[i-1][1],
                                self.trail[i][0], self.trail[i][1] )
        if self.radiation:
            painter.setPen(QColor(255, 0, 0))
            painter.setBrush(QColor(255,0,0))
        else:
            painter.setPen(QColor(53, 100, 75))
            painter.setBrush(QColor(126,210,163))

        
        painter.drawEllipse(self.laser_x-3 , self.laser_y -3 , 6, 6) 
        
                       
        self.canvas.setPixmap(self.pixmap)
    def update_laser_position(self, x, y, radiation):
        self.trail.append((x,y))
        self.radiation = radiation
        self.laser_x = x
        self.laser_y = y
        self.draw_laser()    
    
    
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LaserGUI()
    window.show()
    sys.exit(app.exec())