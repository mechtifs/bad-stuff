import os
import json
import time
import threading
from hthread import HThread


MAX_THREADS = 256

base_url = 'https://www.hacg.mom/wordpress/{}/'

def info():
    while True:
        time.sleep(2)
        try:
            index = threading.enumerate()[2].index
            print('*', threading.active_count(), index)
            with open('old_last', 'w') as f:
                f.write(str(index))
        except IndexError:
            pass

def start():
    try:
        with open('old.json', 'r') as f:
            results = json.loads(f.read())
    except:
        with open('old.json', 'w') as f:
            json.dump({}, f)
            results = {}
    try:
        with open('old_last', 'r') as f:
            start = int(f.read())
    except:
        start = 0

    for i in range(start, 55000):
        while True:
            if threading.active_count() < MAX_THREADS:
                break
            else:
                time.sleep(1)
        if str(i) in results:
            continue
        thread = HThread(base_url, 'old.json', i)
        thread.start()

    while True:
        if threading.active_count() == 2:
            with open('old.json', 'r') as f:
                results = json.loads(f.read())
            results = {k: results[k] for k in sorted(results.keys(), key=lambda x: int(x))}
            with open('old.json', 'w') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            os._exit(0)
        time.sleep(5)


if __name__ == '__main__':
    threading.Thread(target=info).start()
    start()
