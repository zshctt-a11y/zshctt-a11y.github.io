# -*- coding: utf-8 -*-
"""Generate images.js (base64 webp map) + products-data.js (models with full configs)."""
import base64, glob, os, json, re, openpyxl

# images.js
imgs = {}
for f in sorted(glob.glob('webp/*.webp')):
    key = os.path.basename(f).replace('.webp', '')
    imgs[key] = 'data:image/webp;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
with open('images.js', 'w', encoding='utf-8') as fp:
    fp.write('const IMG = ' + json.dumps(imgs) + ';\n')
print('images.js keys:', len(imgs), 'size:', os.path.getsize('images.js'))

# products-data.js — reuse parsing from build_pages
wb = openpyxl.load_workbook('quotation.xlsx', read_only=True)
cat = wb['Catalogue']
vals = {}
for ri, row in enumerate(cat.iter_rows(min_row=1, max_row=63, max_col=8, values_only=True), start=1):
    for ci, v in enumerate(row, start=1):
        vals[(ri, ci)] = v
prices, headline = {}, {}
for (r, col), v in list(vals.items()):
    if not v or not isinstance(v, str):
        continue
    spec, price = vals.get((r + 1, col)), vals.get((r + 2, col))
    if spec and price is not None:
        try:
            p = float(str(price).replace(',', ''))
        except ValueError:
            continue
        prices[v.strip()] = p
        headline[v.strip()] = [x.strip() for x in str(spec).split('|')]

spec_ws = wb['Specifications']
HDR = ["Configuration", "Motor", "Battery", "Controller", "Max speed", "Range",
       "Brakes / Suspension", "Tyre", "Charging", "Gross weight", "Package L*W*H (cm)",
       "Container loading", "Certification"]
configs = {}
for row in spec_ws.iter_rows(min_row=1, max_row=65, max_col=16, values_only=True):
    first = str(row[0] or '')
    if first in ('A', 'B', 'C') and row[2]:
        name = str(row[2]).strip()
        cfg = {}
        for i, h in enumerate(HDR):
            v = row[3 + i] if 3 + i < len(row) else None
            cfg[h] = str(v).strip().replace('\n', ' / ') if v not in (None, '', '-') else ''
        cfg['_line'] = first
        configs.setdefault(name, []).append(cfg)

def slug(n):
    if n == "SMD-Z1 Pro+":
        return "smd-z1-pro-plus"
    return re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')

CERTS = {
 'A': ["CE-EN17128", "CE-MD", "CE-RED", "CE-ROHS", "UL2272", "FCC ID", "UL2271 Battery", "IEC 62133", "UN38.3", "EU Battery Regulation"],
 'B': ["CE", "ROHS", "UN38.3 Battery", "MSDS", "UL2272 on request"],
 'C': ["CE", "ROHS", "EN15194 (pedal-assist)", "UN38.3 Battery", "MSDS"],
}
models = []
for name, p in prices.items():
    cfgs = configs.get(name, [])
    line = cfgs[0]['_line'] if cfgs else 'C'
    models.append({
        'name': name, 'slug': slug(name), 'line': line, 'price': p,
        'img': slug(name), 'headline': headline.get(name, []),
        'configs': [{k: v for k, v in c.items() if not k.startswith('_')} for c in cfgs],
        'certs': CERTS[line],
    })
with open('products-data.js', 'w', encoding='utf-8') as fp:
    fp.write('const MODELS = ' + json.dumps(models, ensure_ascii=False) + ';\n')
print('products-data.js models:', len(models), 'size:', os.path.getsize('products-data.js'))
