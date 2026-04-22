import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tqdm import tqdm

# ---------------- CLI ----------------
parser = argparse.ArgumentParser(description="ZeroClick System - Port Scanner")
parser.add_argument("target")
parser.add_argument("--start", type=int, default=1)
parser.add_argument("--end", type=int, default=1024)
parser.add_argument("--threads", type=int, default=150)

args = parser.parse_args()

target = args.target
start_port = args.start
end_port = args.end
threads = args.threads

results = []

print(f"\nTarget: {target}")
print(f"Range: {start_port}-{end_port}")
print(f"Threads: {threads}")
print("-" * 60)

# ---------------- SERVICE ----------------
def get_service(port):
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"

# ---------------- SCAN ----------------
def scan_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)

            if s.connect_ex((target, port)) == 0:
                service = get_service(port)

                return {
                    "port": port,
                    "service": service
                }

    except:
        pass

    return None

# ---------------- EXECUTION ----------------
ports = range(start_port, end_port + 1)

with ThreadPoolExecutor(max_workers=threads) as executor:
    futures = {executor.submit(scan_port, p): p for p in ports}

    for future in tqdm(as_completed(futures),
                       total=len(futures),
                       desc="Scanning"):

        result = future.result()

        if result:
            line = f"[OPEN] {result['port']} | {result['service']}"
            print(line)
            results.append(result)

# ---------------- SAVE REPORT ----------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

txt_file = f"scan_{target}_{timestamp}.txt"

with open(txt_file, "w") as f:
    f.write(f"ZeroClick System Scan Report\n")
    f.write(f"Target: {target}\n")
    f.write(f"Time: {datetime.now()}\n\n")

    for r in results:
        f.write(f"{r['port']} | {r['service']}\n")

print("\nScan completed.")
print(f"Open ports: {len(results)}")
print(f"Report saved: {txt_file}")
