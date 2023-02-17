import json

with open('old.json', 'r') as f:
    old = json.load(f)
with open('new.json', 'r') as f:
    new = json.load(f)

all = [
    {
        'title': v['title'],
        'url': 'https://www.hacg.mom/wordpress/{}/'.format(k),
        'time': v['time'],
        'categories': [i for i in v['categories'] if '视频' not in i],
        'tags': v['tags'],
        'magnets': v['magnets']
    } for k, v in old.items()
]

for k, v in new.items():
    for i in all:
        if i['title'] == v['title']:
            i['url'] = 'https://www.hacg.mom/wp/{}.html'.format(k)
            i['time'] = v['time']
            i['tags'] = list(set(i['tags']+v['tags']))
            i['categories'] = list(set(i['categories']+v['categories']))
            i['magnets'] = list(set(i['magnets']+v['magnets']))
            break
    else:
        all.append({
            'title': v['title'],
            'url': 'https://www.hacg.me/wp/{}.html'.format(k),
            'time': v['time'],
            'categories': v['categories'],
            'tags': v['tags'],
            'magnets': v['magnets']
        })

all.sort(key=lambda x: x['time'])
with open('all.json', 'w') as f:
    json.dump(all, f, ensure_ascii=False, indent=2)
