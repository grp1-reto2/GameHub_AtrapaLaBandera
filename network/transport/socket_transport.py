import queue, socket, threading, json

class SocketTransport:
    def __init__(self, ip, port, is_server=False):
        self.host = ip
        self.port = port
        self.is_server = is_server
        self.sock = None
        self.thread_recv = None
        self.running = False
        self.incoming = queue.Queue()

        self.clients = [] # Si es server

    def start(self):
        self.sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.is_server:
            self.sock.bind((self.host, self.port))
            self.sock.listen()

            self.running = True
            threading.Thread(target=self._accept_clients,daemon=True).start()

        else:
            self.sock.connect((self.host, self.port))
            self.running = True
            self.thread_recv = threading.Thread(target=self._recv_loop, args=(self.sock,), daemon=True)
            self.thread_recv.start()

    def _accept_clients(self):
        # Crea un thread por cada conexión aceptada.
        while self.running:
            client_sock, addr = self.sock.accept() #type: ignore => Nunca será None
            self.clients.append(client_sock)
            threading.Thread(target=self._recv_loop, args=(client_sock,), daemon=True).start()

    def _recv_loop(self, sock):
        # loop para recibir mensajes.
        while self.running:
            try:
                data = sock.recv(1024)

                if not data: break

                msg = json.loads(data.decode())
                
                self.incoming.put((sock, msg)) # Mete el mensaje en la queue.
            
            except Exception as e:
                print("Transport recv error:", e)
                break

    def send(self, msg, sock=None): # sock por ahora no lo usa. 
        data = json.dumps(msg).encode

        if self.is_server:
            for c in self.clients:
                try:
                    c.sendall(data)
                except:
                    pass

        else: 
            self.sock.sendall(data) #type: ignore => Nunca será None

    def get_incoming_msgs(self):
        list_msg = []

        while not self.incoming.empty():
            list_msg.append(self.incoming.get())

        return list_msg
    
    def stop(self):
        self.running = False
        
        if self.sock: self.sock.close()

        for c in getattr(self, "clients", []):
            c.close()
