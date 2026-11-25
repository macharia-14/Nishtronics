#!/usr/bin/env python3
"""
Turn raw product photos into small WebP files the site picks up automatically.
A real photo replaces that product's drawn illustration (images/products/<id>.svg).

1. Put photos in images/_incoming/ named after the product id:   kw-6x9-kfc1669s.jpg
2. Run:   pip install pillow     (once)
          python tools/prepare-images.py
3. Output goes to images/products/<id>.webp  (max 800px, targeted under ~100 KB), and
   images/products/index.json is rewritten so the site knows which products have a photo.

  python tools/prepare-images.py --missing     # list products that still have no photo

Gallery tiles and blog covers work the same way, and are cropped to the right shape:
  images/_incoming/gallery/gal-car-1.jpg   ->  images/gallery/gal-car-1.webp   (900x675, 4:3)
  images/_incoming/blog/rms-vs-peak-power.jpg -> images/blog/rms-vs-peak-power.webp   (1200x630)
Name the photo after the file it should replace (see the file names in images/gallery and images/blog).

Deploy images/products/ but NOT images/_incoming/ (the raw originals are large).
"""
import json, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(root)
ids = [p['id'] for p in json.load(open('data/products.json', encoding='utf-8'))]
OUT, INC = 'images/products', 'images/_incoming'

if '--missing' in sys.argv:
    miss = [i for i in ids if not os.path.exists(f'{OUT}/{i}.webp')]
    print(f'{len(miss)} of {len(ids)} products still use the drawn illustration (no real photo):'); print('\n'.join(miss)); sys.exit()

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
# gallery tiles and blog covers: crop to a fixed shape, keep the file name of the image being replaced
def crop_folder(sub, out_dir, size, label):
    src = f'{INC}/{sub}'
    if not os.path.isdir(src): return 0
    n = 0
    for fn in sorted(os.listdir(src)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp'): continue
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(f'{src}/{fn}')).convert('RGB'), size, Image.LANCZOS)
        out = f'{out_dir}/{stem}.webp'
        im.save(out, 'WEBP', quality=78, method=6)
        print(f'OK    {label}/{stem}.webp  {size[0]}x{size[1]}  {os.path.getsize(out) // 1024} KB')
        n += 1
    return n
extra = crop_folder('gallery', 'images/gallery', (900, 675), 'gallery') + crop_folder('blog', 'images/blog', (1200, 630), 'blog')
photos = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith('.webp'))
json.dump(photos, open(f'{OUT}/index.json', 'w'))
print(f'\n{done} product photos + {extra} gallery/blog images converted, {skipped} skipped. Missing photos: {len([i for i in ids if not os.path.exists(f"{OUT}/{i}.webp")])} of {len(ids)}')
