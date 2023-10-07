import socket
import select

class Dispatcher:
    def __init__(self):
        self.handlers = []

    def get_handler(self, filter):
        for func, data in self.handlers:
            if data == filter:
                return func
        return None

    def add_handler(self, func, filter):
        self.handlers.append((func, filter))

class Resolver:

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def handle(self, sock):
        try:
            chunks = []
            while True:
                received = sock.recv(1024)
                chunks.append(received.decode())
                if len(received) < 1024:
                    break
            data = ''.join(chunks)
            type = data.split()[0]
            path = data.split()[1]
            rawheaders = data.split("\r\n")[1:-2:]
            headers = {}
            for head in rawheaders:
                head = head.split(": ")
                if len(head) > 1:
                    headers[head[0]] = head[1]
            rawpayload = data.split("\r\n\r\n")[1].split("&")
            payload = {}
            for load in rawpayload:
                load = load.split("=")
                if len(load) > 1:
                    payload[load[0]] = load[1]

            func = self.dispatcher.get_handler({"type": type, "path": path})

            if func:
                argcount = func.__code__.co_argcount

                if argcount == 0:
                    return "HTTP/1.0 200 OK\r\n\r\n" + str(func())
                if argcount == 1:
                    return "HTTP/1.0 200 OK\r\n\r\n" + str(func(payload))
                if argcount == 2:
                    return "HTTP/1.0 200 OK\r\n\r\n" + str(func(payload, headers))
                if argcount > 2:
                    print("\u001b[33mToo much arguments, got\u001b[0m", argcount, "\u001b[31m when max is \u001b[0m2")
            else:
                return "HTTP/1.0 404 Not Found"
        except Exception as e:
            print("\u001b[31mException raised:\u001b[0m", e)
            return "HTTP/1.0 500 Internal Server Error"

    def polling(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen()
        server.setblocking(False)

        print("\u001b[35mServer started")
        print("\u001b[35mIP address:\u001b[0m", f"{ip}:{port}")

        rlist = [server]
        while True:
            readable, writable, errored = select.select(rlist, [], [])
            for sock in readable:
                if sock is server:
                    client, address = server.accept()
                    client.setblocking(False)
                    rlist.append(client)
                    ip, port = address
                    print(f"\u001b[32mReceived request, IP: \u001b[0m{ip}:{port}")
                else:
                    ip, port = sock.getpeername()
                    print(f"\u001b[34mData received from \u001b[0m{ip}:{port}")
                    sock.send(self.handle(sock).encode())
                    sock.close()
                    rlist.remove(sock)



