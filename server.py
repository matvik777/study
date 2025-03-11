import socket
import threading
import time
import json

class LaserServer:
    def __init__(self, host="127.0.0.1", tcp_port=5000, udp_port=5001):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.x, self.y = 250, 250
        self.radiation = False
        self.move_id = 1
        
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("127.0.0.1", 5000))
        self.tcp_server.listen(5)
        
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #флаг-Event и ссылка на поток
        self.stop_event = threading.Event()
        self.current_move_tread = None
        
        
    def handle_client(self, client_socket, addr):
        try:
            print(f"[SERVER] Подключился клиент {addr}")  # Новое сообщение о подключении
            data = client_socket.recv(1024).decode("utf-8")
            command = json.loads(data)
            print(f"[SERVER] Получил команду: {command}")
            
            if command["cmd"] == "move":
                x, y, speed = command["x"], command["y"], command["speed"]
                self.start_move(x,y, speed)

                client_socket.send(json.dumps({"status": "OK"}).encode("utf-8"))
            elif command["cmd"] == "toggle_laser":
                self.radiation = not self.radiation
                client_socket.send(json.dumps({"status": self.radiation}).encode("utf-8"))
                print(f"Laser on? {self.radiation}")
        except Exception as e:
            print(f"[ERROR] : {e}")
            
        finally:
            client_socket.close()
            
    def start_move(self,target_x, target_y, speed):
        
        self.stop_event.set()
        if self.current_move_tread and self.current_move_tread.is_alive():
            self.current_move_tread.join()
        
        self.stop_event.clear()
        
        current_id = self.move_id
        self.move_id += 1
        
        
        self.current_move_tread = threading.Thread(target=self.run_move, args=(target_x, target_y, speed, current_id), daemon=None)
        self.current_move_tread.start()
    
    
    
    def run_move(self, target_x, target_y, speed, move_id):
        path = self.bresenham_line(self.x, self.y , target_x, target_y)
        interval = 0.1/speed
        
        for x, y in path:
            
            if self.stop_event.is_set():
                return
            
            self.x, self.y = x, y
            status = json.dumps({
                "x": self.x,
                "y": self.y,
                "radiation": self.radiation,
                "move_id": move_id
                })
            self.udp_server.sendto(status.encode("utf-8"), (self.host, self.udp_port))
            time.sleep(interval)
    
    
    
           
    # def move_laser(self, target_x, targer_y, speed):
    
    #     path = self.bresenham_line(self.x, self.y , target_x, targer_y)
    #     interval = 0.1/speed
        
    #     for x, y in path:
    #         self.x, self.y = x, y
    #         status = json.dumps({"x": self.x, "y": self.y})
    #         self.udp_server.sendto(status.encode("utf-8"), (self.host, self.udp_port))
    #         time.sleep(interval)
    
    def bresenham_line(self, x1, y1, x2, y2):
        
        """Алгоритм Брезенхэма: возвращает список точек для движения"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return points
    
    def start(self):
        
        print(f"Сервер слушает TCP {self.host}: {self.tcp_port}")
        while True:
            client_socket, addr = self.tcp_server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
if __name__ == "__main__":
    server = LaserServer()
    server.start()
        
    
  