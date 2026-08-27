# -*- coding: utf-8 -*-
"""Final image set: white-bg images -> plain compressed webp; black-bg images -> transparent cutout; logo -> plain."""
from PIL import Image
import glob, os

CUTOUTS = {'mt-x-pro', 'zm22-single-motor'}  # black-bg originals, already cleanly cut out in webp/
os.makedirs('final', exist_ok=True)

for f in sorted(glob.glob('products/img/*.jpg')) + ['logo.jpg']:
    key = os.path.basename(f).replace('.jpg', '')
    out = 'final/' + key + '.webp'
    if key in CUTOUTS:
        im = Image.open(f'webp/{key}.webp')  # keep cutout
    else:
        im = Image.open(f).convert('RGB')    # keep white bg as-is
        im.thumbnail((460, 460))
    im.save(out, 'WEBP', quality=80)
    print(key, 'cutout' if key in CUTOUTS else 'plain', os.path.getsize(out), 'B')
