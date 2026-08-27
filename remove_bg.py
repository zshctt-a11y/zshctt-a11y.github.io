# -*- coding: utf-8 -*-
"""Remove white OR black backgrounds from product images -> transparent webp."""
from PIL import Image, ImageDraw, ImageFilter
import glob, os

os.makedirs('webp', exist_ok=True)

def corner_bg(im):
    px = im.convert('RGB')
    w, h = px.size
    pts = [(2,2),(w-3,2),(2,h-3),(w-3,h-3),(w//2,2),(2,h//2),(w-3,h//2),(w//2,h-3)]
    vals = [px.getpixel(p) for p in pts]
    avg = tuple(sum(c[i] for c in vals)//len(vals) for i in range(3))
    return avg

def process(f):
    im = Image.open(f).convert('RGB')
    bg = corner_bg(im)
    lum = sum(bg)/3
    rgba = im.convert('RGBA')
    # flood fill from many border seeds; fill color alpha=0
    w, h = rgba.size
    seeds = []
    step = 8
    for x in range(0, w, step):
        seeds += [(x,0),(x,h-1)]
    for y in range(0, h, step):
        seeds += [(0,y),(w-1,y)]
    thresh = 60 if lum > 128 else 50
    for s in seeds:
        p = rgba.getpixel(s)
        if p[3] != 0 and abs(p[0]-bg[0])+abs(p[1]-bg[1])+abs(p[2]-bg[2]) < thresh*3:
            ImageDraw.floodfill(rgba, s, (0,0,0,0), thresh=thresh)
    # smooth alpha edges
    a = rgba.getchannel('A').filter(ImageFilter.GaussianBlur(1.2))
    rgba.putalpha(a)
    rgba.thumbnail((460,460))
    out = 'webp/' + os.path.basename(f).replace('.jpg','.webp')
    rgba.save(out, 'WEBP', quality=80)
    return bg, os.path.getsize(out)

for f in sorted(glob.glob('products/img/*.jpg')) + ['logo.jpg']:
    bg, size = process(f)
    kind = 'white' if sum(bg)/3 > 128 else 'black'
    print(f'{f}: bg={bg} ({kind}) -> {size}B')
