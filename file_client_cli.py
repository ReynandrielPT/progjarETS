import socket
import json
import base64
import argparse
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor

server_address = ('172.16.16.101', 8889)

def send_command(command_str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            sock.sendall(command_str.encode() + b"\r\n\r\n")
            data = ""
            while True:
                chunk = sock.recv(65536)
                if chunk:
                    data += chunk.decode()
                    if data.endswith("\r\n\r\n"):
                        break
                else:
                    break
            return json.loads(data[:-4])
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        print(f"File {hasil['data_namafile']} berhasil didownload")
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filepath):
    if not os.path.exists(filepath):
        return {"status": "ERROR", "data": f"File not found: {filepath}"}
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        filename = os.path.basename(filepath)
        start = time.time()
        res = send_command(f"UPLOAD {filename} {b64}")
        dur = time.time() - start
        tp = len(raw) / dur if dur > 0 else 0
        res.update({"filename": filename, "duration": dur, "throughput": tp})
        return res
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}

def get_indexed_filename(filename):
    if not os.path.exists(filename):
        return filename
    base, ext = os.path.splitext(filename)
    index = 1
    while True:
        new_name = f"{base}_{index}{ext}"
        if not os.path.exists(new_name):
            return new_name
        index += 1

def remote_download(filename):
    start = time.time()
    res = send_command(f"GET {filename}")
    dur = time.time() - start
    if res.get('status') == 'OK':
        try:
            data = base64.b64decode(res.get('data_file', ''))
            save_filename = get_indexed_filename(filename)
            with open(save_filename, 'wb') as f:
                f.write(data)
            tp = len(data) / dur if dur > 0 else 0
            res.update({"filename": save_filename, "duration": dur, "throughput": tp})
        except Exception as e:
            return {"status": "ERROR", "data": str(e)}
    else:
        res.update({"filename": filename, "duration": dur, "throughput": 0})
    return res



def task(op, filepath, worker_id):
    print(f"[Worker-{worker_id}] Starting {op} on {filepath}")
    if op == 'upload':
        return remote_upload(filepath)
    elif op == 'download':
        return remote_download(filepath)
    else:
        return {"status": "ERROR", "data": "Invalid operation"}

def main():
    global server_address
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='172.16.16.101')
    parser.add_argument('--port', type=int, default=8889)
    parser.add_argument('--operation', choices=['upload', 'download'], required=True)
    parser.add_argument('--files', nargs='+', required=True)
    parser.add_argument('--pool', type=int, default=1)
    args = parser.parse_args()

    server_address = (args.host, args.port)

    if len(args.files) == 1 and args.pool > 1:
        filepath = args.files[0]
        tasks = [filepath] * args.pool
    else:
        tasks = args.files[:args.pool]

    with ThreadPoolExecutor(max_workers=args.pool) as executor:
        futures = []
        for i, filepath in enumerate(tasks):
            futures.append(executor.submit(task, args.operation, filepath, i+1))

        for f in futures:
            print(json.dumps(f.result()))

if __name__ == '__main__':
    main()
