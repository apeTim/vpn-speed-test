import time
import os
import psycopg2
import base64
import subprocess
from datetime import datetime
from speed_test import speed_test_download, speed_test_instagram

DB = os.environ.get("DATABASE_URL") or "postgres://user:password@127.0.0.1/okvpn"
LOCAL_PORT = 1100
DELAY = 60 * 3600
TESTS = 2
ROUND = 3
SLEEP = 10


def run():
    conn = psycopg2.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT stk.key FROM stats.servers_test_keys as stk JOIN servers ON stk.server = servers.ip_address WHERE servers.is_active = true")
    keys = cur.fetchall()

    for key_row in keys:
        key = key_row[0]
        keypass = key.split("@")[0].split("//")[1]
        server = key.split("@")[1].split(":")[0]
        port = key.split("@")[1].split(":")[1].split("/?")[0]
        method = base64.b64decode(keypass).decode('utf-8').split(':')[0]
        password = base64.b64decode(keypass).decode('utf-8').split(':')[1]

        print(f"Measuring {server}")

        ss_process = subprocess.Popen(
            ["ss-local", "-s", server, "-p", port, "-k", password, "-l", str(LOCAL_PORT), "-m", method],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        time.sleep(SLEEP)

        try:
            download_speed_total = 0
            instagram_speed_total = 0
            for i in range(TESTS):
                download_speed_total += speed_test_download(LOCAL_PORT)
                instagram_speed_total += speed_test_instagram(LOCAL_PORT)

            download_speed = round(download_speed_total / TESTS, ROUND)
            instagram_speed = round(instagram_speed_total / TESTS, ROUND)
            print(f"Download speed: {download_speed} Mbps, Instagram speed: {instagram_speed} sec")

            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
            cur.execute("INSERT INTO stats.servers_test_results (server, download_speed_mbps, instagram_speed_sec, created_at) VALUES (%s, %s, %s, %s)",
                        (server, download_speed, instagram_speed, now))
            conn.commit()
        except Exception as e:
            print(e)
            time.sleep(SLEEP)
        finally:
            ss_process.kill()
            time.sleep(SLEEP)

    cur.close()
    conn.close()


while True:
    print("Starting measuring")
    run()
    print("Succesfully measured")
    time.sleep(DELAY)
