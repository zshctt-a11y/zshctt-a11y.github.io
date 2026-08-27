# -*- coding: utf-8 -*-
import subprocess, glob, json, re, os, time
urls = json.load(open('cdn_urls.json')) if os.path.exists('cdn_urls.json') else {}
files = ['logo.jpg'] + sorted(glob.glob('products/img/*.jpg'))
files = [f.replace(os.sep, '/') for f in files]
for f in files:
    if urls.get(f, '').startswith('https://i.imgur'):
        continue
    ok = False
    for attempt in range(5):
        out = subprocess.run(['curl', '-s', '-H', 'Authorization: Client-ID 546c25a59c58ad7',
                              '-F', 'image=@' + f, 'https://api.imgur.com/3/image'],
                             capture_output=True, text=True, timeout=180)
        m = re.search(r'"link":"(https:\\/\\/i\.imgur\.com\\/[^"]+)"', out.stdout)
        if m:
            urls[f] = m.group(1).replace('\\/', '/')
            print('OK ', f, '->', urls[f], flush=True)
            ok = True
            break
        print('retry', attempt, f, out.stdout[:60].replace('\n', ' '), flush=True)
        time.sleep(4 * (attempt + 1))
    if not ok:
        print('FAILED', f, flush=True)
    time.sleep(1.5)
json.dump(urls, open('cdn_urls.json', 'w'))
good = len([u for u in urls.values() if u.startswith('https://i.imgur')])
print('uploaded', good, '/', len(files))
