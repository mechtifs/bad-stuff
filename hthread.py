import re
import html
import json
import datetime
import requests
import threading
import traceback


title_re = re.compile(r'<title>(.+) \| .+?<\/title>')
content_re = re.compile(r'entry-content([\S\s]+?).entry-content')
magnet_re = re.compile(r'[^/=+0-9a-fA-F]([0-9a-fA-F]{32}|[0-9a-fA-F]{40})[^/=+0-9a-fA-F]')
category_re = re.compile(r'rel="category tag">(.+?)<\/a>')
tag_re = re.compile(r'rel="tag">(.+?)<\/a>')
time_re = re.compile(r'datetime="(.+?)"')

class HThread(threading.Thread):
    lock = threading.Lock()

    def __init__(self, url, json_file, index, verbose=False):
        super().__init__()
        self.base_url = url
        self.json_file = json_file
        self.index = index
        if verbose:
            self.log = print
        else:
            self.log = lambda *args, **kwargs: None

    def run(self):
        ret = self.main()
        if ret:
            self.lock.acquire()
            with open(self.json_file, 'r') as f:
                results = json.loads(f.read())
            results.update(ret)
            with open(self.json_file, 'w') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.lock.release()

    def main(self):
        while True:
            try:
                r = requests.get(self.base_url.format(self.index), allow_redirects=False, timeout=5)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
                continue
            if r.status_code < 500:
                break
        if r.status_code != 200:
            self.log(self.index, r.status_code)
            return

        r.encoding = 'utf-8'
        try:
            content = content_re.search(r.text).group(1)
        except AttributeError:
            self.log(self.index, 'Invalid')
            return

        magnets = ['magnet:?xt=urn:btih:'+html.unescape(x).lower() for x in set(magnet_re.findall(content))]
        if not magnets:
            self.log(self.index, 'None')
            return
        time = datetime.datetime.strptime(time_re.search(r.text).group(1), '%Y-%m-%dT%H:%M:%S%z').astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        title = html.unescape(title_re.search(r.text).group(1)).strip()
        categories = [html.unescape(category) for category in category_re.findall(r.text)]
        tags = [html.unescape(tag).strip(' |') for tag in tag_re.findall(r.text)]
        if len(tags) == 1:
            tags = tags[0].split('，')
        self.log(self.index, title)

        return {
            self.index: {
                'title': title,
                'time': time,
                'categories': categories,
                'tags': tags,
                'magnets': magnets
            }
        }
