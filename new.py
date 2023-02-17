import os
import re
import json
import time
import requests
import threading
from hthread import HThread


MAX_THREADS = 32

base_url = 'https://www.hacg.mom/wp/{}.html'

def info():
    while True:
        time.sleep(2)
        try:
            index = threading.enumerate()[2].index
            print('*', threading.active_count(), index)
            with open('new_last', 'w') as f:
                f.write(str(index))
        except IndexError:
            pass

def start():
    try:
        with open('new.json', 'r') as f:
            results = json.loads(f.read())
    except:
        with open('new.json', 'w') as f:
            json.dump({}, f)
            results = {}
    try:
        with open('new_last', 'r') as f:
            start = int(f.read())
    except:
        start = 0

    r = requests.get(base_url.format(0))
    articles = re.findall(r'class="post-(.+?)"', r.text)
    end = 0
    for article in articles:
        if 'sticky' not in article:
            end = int(article.split()[0])
            break

    for i in range(start, end+1):
        while True:
            if threading.active_count() < MAX_THREADS:
                break
            else:
                time.sleep(1)
        if str(i) in results:
            continue
        thread = HThread(base_url, 'new.json', i)
        thread.start()

    while True:
        if threading.active_count() == 2:
            with open('new.json', 'r') as f:
                results = json.loads(f.read())
            results = {k: results[k] for k in sorted(results.keys(), key=lambda x: int(x))}
            with open('new.json', 'w') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            os._exit(0)
        time.sleep(5)


if __name__ == '__main__':
    threading.Thread(target=info).start()
    start()
