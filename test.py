import subprocess
import time
import csv
import argparse
import json
import os

CLIENT_POOL = [50]
SIZES = [10, 50, 100]
OPS = ['upload']

FIELDNAMES = [
    'Nomor', 'Operasi', 'Volume',
    'ClientPool', 'TimePerClient', 'ThroughputPerClient',
    'ClientSuccess', 'ClientFail'
]

parser = argparse.ArgumentParser()
parser.add_argument('--server-host', default='172.16.16.101')
parser.add_argument('--server-port', type=int, default=50000)
args = parser.parse_args()

HOST = args.server_host
PORT = args.server_port

def run_client(pool, op, size):
    file_arg = f'test_data/file{size}MB.bin' if op == 'upload' else f'file{size}MB.bin'
    
    cmd = [
        'python3', 'file_client_cli.py',
        '--host', HOST,
        '--port', str(PORT),
        '--operation', op,
        '--files', file_arg,
        '--pool', str(pool)
    ]

    start = time.time()
    output = subprocess.check_output(cmd).decode().strip()
    elapsed = time.time() - start
    time.sleep(20)
    succ = 0
    fail = 0
    total_tp = 0.0
    downloaded_files = []

    for line in output.splitlines():
        try:
            res = json.loads(line)
            if res.get("status").lower() == "ok":
                succ += 1
                total_tp += float(res.get("throughput", 0))
                if op == "download":
                    downloaded_files.append(res.get("filename", ""))
            else:
                fail += 1
        except json.JSONDecodeError:
            continue

    for fname in downloaded_files:
        if fname.startswith("file") and fname.endswith(".bin"):
            try:
                os.remove(fname)
            except FileNotFoundError:
                pass

    return succ, fail, elapsed, total_tp / succ if succ > 0 else 0.0


with open('results_client.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    no = 1
    for op in OPS:
        for size in SIZES:
            for cli_pool in CLIENT_POOL:
                print(f"Menjalankan test {no}: operasi={op}, size={size}MB, pool={cli_pool}")
                cs, cf, tpc, tp = run_client(cli_pool, op, size)
                if cs < cli_pool:
                    print(f"Test {no} gagal: hanya {cs} dari {cli_pool} client berhasil. Pengujian dihentikan.")
                    
                writer.writerow({
                    'Nomor': no,
                    'Operasi': op,
                    'Volume': size,
                    'ClientPool': cli_pool,
                    'TimePerClient': round(tpc, 3),
                    'ThroughputPerClient': round(tp, 3),
                    'ClientSuccess': cs,
                    'ClientFail': cf
                })
                no += 1

print("Client stress test selesai, hasil disimpan di results_client.csv")

