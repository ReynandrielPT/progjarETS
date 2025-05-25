import os
import socket
import threading
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from file_protocol import FileProtocol

TIMEOUT_IDLE = 300
fp = FileProtocol()
STORAGE_DIR = './files'

def get_indexed_filename(filename):
    base, ext = os.path.splitext(filename)
    candidate = filename
    index = 1
    while os.path.exists(os.path.join(STORAGE_DIR, candidate)):
        candidate = f"{base}_{index}{ext}"
        index += 1
    return candidate

def handle_client_request(connection):

    try:
        data_b = ""
        while True:
            data = connection.recv(4096)
            if not data:
                break
            data_b += data.decode()

            if data_b.endswith("\r\n\r\n"):
                break

        if data_b:
            d = data_b[:-4]

            if d.startswith("UPLOAD "):
                try:
                    command, rest = d.split(' ', 1)
                    filename, filedata = rest.split(' ', 1)
                    indexed_filename = get_indexed_filename(filename)
                    d = f"{command} {indexed_filename} {filedata}"
                    logging.warning(f"UPLOAD request, filename disesuaikan: {filename} -> {indexed_filename}")
                except Exception as e:
                    logging.error(f"Error parsing UPLOAD request: {e}")

            hasil = fp.proses_string(d)
            hasil += "\r\n\r\n"
            connection.sendall(hasil.encode())

    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        connection.close()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        handle_client_request(self.connection)

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', mode='thread', pool_size=5):
        super().__init__()
        self.ipinfo = (ipaddress, 8889)
        self.the_clients = []
        self.mode = mode
        self.pool_size = pool_size
        self.executor = None

        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self.mode == 'threadpool':
            self.executor = ThreadPoolExecutor(max_workers=self.pool_size)
        elif self.mode == 'processpool':
            self.executor = ProcessPoolExecutor(max_workers=self.pool_size)

    def run(self):
        logging.warning(f"Server berjalan di {self.ipinfo}, mode={self.mode}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(100)
        self.my_socket.settimeout(1)
        last_active = time.time()	
        try:
            while True:
                try:
                    connection, client_address = self.my_socket.accept()
                    logging.warning(f"Connection dari {client_address}")
                    last_active = time.time()
                    if self.mode in ['threadpool', 'processpool']:
                        self.executor.submit(handle_client_request, connection)
                    else:
                        clt = ProcessTheClient(connection, client_address)
                        clt.start()
                        self.the_clients.append(clt)

                except socket.timeout:
                    if time.time() - last_active > TIMEOUT_IDLE:
                       logging.warning("Tidak ada koneksi dalam 5 detik, server shutdown...")
                       break

        except KeyboardInterrupt:
            logging.warning("Server dihentikan oleh user")
        except Exception as e:
            logging.error(f"Error pada server: {e}")
        finally:
            if self.executor:
                self.executor.shutdown(wait=True)
            self.my_socket.close()
            logging.warning("Server berhenti dengan sempurna.")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['thread', 'threadpool', 'processpool'], default='thread')
    parser.add_argument('--poolsize', type=int, default=5)
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')

    svr = Server(ipaddress='0.0.0.0', mode=args.mode, pool_size=args.poolsize)
    svr.start()
    svr.join()

if __name__ == "__main__":
    main()

