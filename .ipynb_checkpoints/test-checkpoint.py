import subprocess
import time
import csv
import argparse

CLIENT_POOL = [1, 5, 50]
SIZES = [10, 50, 100]
OPS = ['upload', 'download']

FIELDNAMES = [
    'Nomor', 'Operasi', 'Volume',
    'ClientPool', 'TimePerClient', 'ThroughputPerClient',
    'ClientSuccess', 'ClientFail'
]

parser = argparse.ArgumentParser()
parser.add_argument('--server-host', default='127.0.0.1')
parser.add_argument('--server-port', type=int, default=8889)
args = parser.parse_args()

HOST = args.server_host
PORT = args.server_port


def run_client(pool, op, size):
    cmd = [
        'python3', 'file_client_cli.py',
        '--host', HOST,
        '--port', str(PORT),
        '--pool', str(pool),
        '--op', op,
        '--size', str(size)
    ]
    start = time.time()
    out = subprocess.check_output(cmd).decode().strip()
    elapsed = time.time() - start
    # parse "Success:x,Fail:y,Time:zz.zz,TP:tt.tt"
    parts = dict(p.split(':') for p in out.split(','))
    succ = int(parts['Success'])
    fail = int(parts['Fail'])
    tp = float(parts['TP'])
    return succ, fail, elapsed, tp

with open('results_client.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    no = 1
    for op in OPS:
        for size in SIZES:
            for cli_pool in CLIENT_POOL:
                cs, cf, tpc, tp = run_client(cli_pool, op, size)
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
