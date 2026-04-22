import asyncio
import socket
import json
from datetime import datetime
from tqdm import tqdm

# ---------------- INPUT ----------------
target = input("Target IP: ")
start_port = int(input("Start port: "))
end_port = int(input("End port: "))

results = []

print(f"\nScanning {target}...")
print("-" * 60)

# ---------------- SERVICE ----------------
def get_service(port):
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"

# ---------------- BANNER ----------------
def grab_banner(sock):
    try:
        sock.settimeout(0.2)
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        return sock.recv(1024).decode(errors="ignore").strip()
    except:
        return ""

# ---------------- ASYNC SCAN ----------------
async def scan_port(port):
    loop = asyncio.get_event_loop()

    def check():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)

            if s.connect_ex((target, port)) == 0:
                service = get_service(port)
                banner = grab_banner(s)
                s.close()

                return {
                    "port": port,
                    "service": service,
                    "banner": banner[:80]
                }

            s.close()
        except:
            pass

        return None

    return await loop.run_in_executor(None, check)

# ---------------- RUN ----------------
async def run():
    tasks = [scan_port(p) for p in range(start_port, end_port + 1)]

    for f in tqdm(asyncio.as_completed(tasks),
                  total=len(tasks),
                  desc="Scanning"):

        result = await f

        if result:
            print(f"[OPEN] {result['port']} | {result['service']}")
            results.append(result)

asyncio.run(run())

# ---------------- SAVE REPORTS ----------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

txt_file = f"scan_{target}_{timestamp}.txt"
json_file = f"scan_{target}_{timestamp}.json"

with open(txt_file, "w") as f:
    for r in results:
        f.write(f"{r['port']} | {r['service']} | {r['banner']}\n")

with open(json_file, "w") as f:
    json.dump(results, f, indent=4)

print("\n" + "-" * 60)
print("Scan completed.")
print(f"Open ports: {len(results)}")
print(f"TXT: {txt_file}")
print(f"JSON: {json_file}")
