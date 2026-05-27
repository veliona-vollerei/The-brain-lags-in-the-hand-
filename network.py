import socket
import threading
import pickle
import sys
import time

class Network:
    def __init__(self):
        self.socket = None
        self.udp_socket = None
        self.is_host = False
        self.connected = False
        self.clients = []          # host: list of (socket, addr, name)
        self.received_data = None
        self.running = False
        self.recv_thread = None
        self.host_game_ready = False
        self.player_name = ""
        self.opponent_name = ""
        self.room_code = ""
        self.broadcast_port = 5556
        self.broadcast_running = False

    # ----- HOST: vừa broadcast vừa tạo server TCP -----
    def start_broadcast(self, room_code, player_name):
        self.is_host = True
        self.room_code = room_code
        self.player_name = player_name
        self.broadcast_running = True
        self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.broadcast_thread.start()
        return self.create_server()

    def _broadcast_loop(self):
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.udp_socket.bind(('', self.broadcast_port))
        except Exception as e:
            print(f"Broadcast error: {e}")
            return
        while self.broadcast_running and self.running:
            data = pickle.dumps({
                "type": "room",
                "room_code": self.room_code,
                "host_ip": self.get_local_ip(),
                "player_count": len(self.clients),
                "host_name": self.player_name
            })
            try:
                self.udp_socket.sendto(data, ('<broadcast>', self.broadcast_port))
            except:
                pass
            time.sleep(2)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    # ----- HOST: tạo server TCP, chờ client -----
    def create_server(self, port=5555):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', port))
            self.socket.listen(2)
            self.running = True
            self.accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            self.accept_thread.start()
            return True
        except Exception as e:
            print(f"Lỗi tạo server: {e}")
            return False

    def _accept_clients(self):
        while self.running and len(self.clients) < 2:
            try:
                client_sock, addr = self.socket.accept()
                data = client_sock.recv(1024)
                rcvd_room, name = pickle.loads(data)
                if rcvd_room != self.room_code:
                    client_sock.send(pickle.dumps({"status": "error", "msg": "Sai mã phòng"}))
                    client_sock.close()
                    continue
                self.clients.append((client_sock, addr, name))
                print(f"Host: Client {name} từ {addr} đã kết nối. ({len(self.clients)}/2)")
                client_sock.send(pickle.dumps({"status": "waiting"}))
                if len(self.clients) == 2:
                    print("Host: Đã đủ 2 client. Bắt đầu trận đấu!")
                    sock1, _, name1 = self.clients[0]
                    sock2, _, name2 = self.clients[1]
                    sock1.send(pickle.dumps({"status": "start", "opponent": name2, "your_name": name1}))
                    sock2.send(pickle.dumps({"status": "start", "opponent": name1, "your_name": name2}))
                    self.host_game_ready = True
                    self._start_relay()
            except:
                break

    def _start_relay(self):
        def relay(from_sock, to_sock):
            try:
                while self.running:
                    data = from_sock.recv(1024)
                    if not data:
                        break
                    to_sock.send(data)
            except:
                pass
        if len(self.clients) >= 2:
            threading.Thread(target=relay, args=(self.clients[0][0], self.clients[1][0]), daemon=True).start()
            threading.Thread(target=relay, args=(self.clients[1][0], self.clients[0][0]), daemon=True).start()

    # ----- CLIENT: quét phòng (UDP) -----
    @staticmethod
    def scan_rooms(timeout=2):
        """Quét các phòng đang broadcast trên mạng LAN"""
        rooms = []
        try:
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp.bind(('', 0))
            udp.settimeout(timeout)
            request = pickle.dumps({"type": "scan"})
            udp.sendto(request, ('<broadcast>', 5556))
            start = time.time()
            while time.time() - start < timeout:
                try:
                    data, addr = udp.recvfrom(1024)
                    msg = pickle.loads(data)
                    if msg.get("type") == "room":
                        rooms.append({
                            "ip": addr[0],
                            "room_code": msg["room_code"],
                            "host_name": msg.get("host_name", "Host"),
                            "player_count": msg.get("player_count", 0)
                        })
                except:
                    pass
            udp.close()
        except:
            pass
        # Loại bỏ trùng theo room_code
        unique = {}
        for r in rooms:
            if r["room_code"] not in unique:
                unique[r["room_code"]] = r
        return list(unique.values())

    # ----- CLIENT: kết nối đến host -----
    def connect_to_server(self, ip, port, room_code, player_name):
        self.is_host = False
        self.player_name = player_name
        self.room_code = room_code
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.socket.send(pickle.dumps((room_code, player_name)))
            data = self.socket.recv(1024)
            resp = pickle.loads(data)
            if resp.get("status") == "waiting":
                self.connected = True
                self.running = True
                self.recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
                self.recv_thread.start()
                return True
            else:
                return False
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            return False

    def _receive_loop(self):
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                self.received_data = pickle.loads(data)
            except:
                break
        self.connected = False

    def send_data(self, data):
        if self.connected:
            try:
                self.socket.send(pickle.dumps(data))
            except:
                pass

    def get_opponent_action(self):
        if self.received_data is not None:
            action = self.received_data
            self.received_data = None
            return action
        return None

    def is_game_started(self):
        if self.is_host:
            return self.host_game_ready
        else:
            if self.received_data and isinstance(self.received_data, dict) and self.received_data.get("status") == "start":
                self.opponent_name = self.received_data.get("opponent", "Opponent")
                self.player_name = self.received_data.get("your_name", self.player_name)
                self.received_data = None
                return True
            return False

    def close(self):
        self.running = False
        self.broadcast_running = False
        if self.udp_socket:
            self.udp_socket.close()
        if self.socket:
            self.socket.close()
        for sock, _, _ in self.clients:
            sock.close()