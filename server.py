import socket
import threading
import time
import json

class LaserServer:
    def __init__(self, host="127.0.0.1", tcp_port=5000, udp_port=5001):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        
        self.x, self.y = 0, 0
        
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("127.0.0.1", 5000))
        self.tcp_server.listen(5)
        
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def handle_client(self, client_socket):
        
        data = client_socket.recv(1024).decode("utf-8")
        command = json.loads(data)
        
        if command["cmd"] == "move":
            x, y, speed = command["x"], command["y"], command["speed"]
            self.move_laser(x,y,speed)

    def move_laser(self, target_x, targer_y, speed):
    
        path = self.bresenham_line(self.x, self.y , target_x, targer_y)
        interval = 0.1/speed
        
        for x, y in path:
            self.x, self.y = x, y
            status = json.dumps({"x": self.x, "y": self.y})
            self.udp_server.sendto(status.encode("utf-8"), (self.host, self.udp_port))
            time.sleep(interval)
    
    def bresenham_line(self, x1, y1, x2, y2):
        
        points = []
        while (x1 != x2) or (y1 != y2):
            points.append((x1, y1))
        
            dx = x2 - x1
            dy = y2 - y1
        
            # Определяем направление
            sx = 1 if dx > 0 else -1
            sy = 1 if dy > 0 else -1
        
            # Смотрим, по какой оси разница больше
            if abs(dx) >= abs(dy):
                x1 += sx
            else:
                y1 += sy
    
        # Добавляем конечную точку
        points.append((x2, y2))
        return points
    
    def start(self):
        
        print(f"Сервер слушает TCP {self.host}: {self.tcp_port}")
        while True:
            client_socket, _ = self.tcp_server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
if __name__ == "__main__":
    server = LaserServer()
    server.start()
        
    
  