#!/usr/bin/env python3
"""
Turn raw product photos into small WebP files the site picks up automatically.

1. Put photos in images/_incoming/ named after the product id:   kw-6x9-kfc1669s.jpg
2. Run:   pip install pillow     (once)
          python tools/prepare-images.py
3. Output goes to images/products/<id>.webp  (max 800px, targeted under ~100 KB).

  python tools/prepare-images.py --missing     # list products that still have no photo

Deploy images/products/ but NOT images/_incoming/ (the raw originals are large).
"""
import json, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(root)
ids = [p['id'] for p in json.load(open('data/products.json', encoding='utf-8'))]
OUT, INC = 'images/products', 'images/_incoming'

if '--missing' in sys.argv:
    miss = [i for i in ids if not os.path.exists(f'{OUT}/{i}.webp')]
    print(f'{len(miss)} of {len(ids)} products have no photo yet:'); print('\n'.join(miss)); sys.exit()

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('Install Pillow first:  pip install pillow')

MAX_PX, TARGET = 800, 100 * 1024
done = skipped = 0
for fn in sorted(os.listdir(INC)):
    stem, ext = os.path.splitext(fn)
    if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp'): continue
    if stem not in ids:
        print(f'SKIP  {fn}: no product with id "{stem}"'); skipped += 1; continue
    im = ImageOps.exif_transpose(Image.open(f'{INC}/{fn}')).convert('RGB')
    im.thumbnail((MAX_PX, MAX_PX))
    for q in (85, 78, 70, 62, 55, 48):
        im.save(f'{OUT}/{stem}.webp', 'WEBP', quality=q, method=6)
        if os.path.getsize(f'{OUT}/{stem}.webp') <= TARGET: break
    kb = os.path.getsize(f'{OUT}/{stem}.webp') // 1024
    print(f'OK    {stem}.webp  {im.size[0]}x{im.size[1]}  {kb} KB' + ('  (over 100 KB, consider a simpler background)' if kb > 100 else ''))
    done += 1
print(f'\n{done} converted, {skipped} skipped. Missing photos: {len([i for i in ids if not os.path.exists(f"{OUT}/{i}.webp")])} of {len(ids)}')
