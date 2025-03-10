import socket
import json
import threading

class LaserClient:
    def __init__(self, host="127.0.0.1", tcp_port= 5000, udp_port = 5001 ):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.gui = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host, self.udp_port))
        threading.Thread(target=self.receive_updates, daemon=True).start()
        
        
        
    def set_gui(self, gui):
        self.gui = gui
           
    def send_move_command(self, x, y, speed):
        command = json.dumps({"cmd": "move", "x": x, "y": y, "speed": speed})
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect((self.host, self.tcp_port))
                tcp_socket.sendall(command.encode("utf-8"))
                # response = tcp_socket.recv(1024).decode("utf-8")
                # print(f"Ответ сервера: {response}") 
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")   
            
    def receive_updates(self):
        while True:
            try:
                data, _ = self.udp_socket.recvfrom(1024)
                status = json.loads(data.decode("utf-8"))
                print(f"Laser: {status}")
                if self.gui:
                    self.gui.update_laser_position(status["x"], status["y"])
            except Exception as e:
                print(f"Error coordinaty : {e}")
if __name__ == "__main__":
    client = LaserClient()
    client.send_move_command(40, 40, 5)       
