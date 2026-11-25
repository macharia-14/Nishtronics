#!/usr/bin/env python3
"""
Packs ONLY the public files into dist/ (and optionally dist.zip) so you upload exactly what the site needs:

    python tools/make-dist.py          # creates dist/
    python tools/make-dist.py --zip    # also creates dist.zip (Cloudflare Pages accepts a folder or a zip)

Left out on purpose: tools/, content/ (blog source), SETUP.md, firestore.rules, *.snippet and
images/_incoming/ (large raw photos). Run it after every change, then upload dist/ again.
"""
import os, shutil, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)

TOP_FILES = [f for f in os.listdir('.') if f.endswith('.html')] + [f for f in ('sitemap.xml', 'robots.txt', 'feed.xml', '_headers', '_redirects') if os.path.exists(f)]
DIRS = ['css', 'js', 'data', 'images', 'blog']

shutil.rmtree('dist', ignore_errors=True)
os.makedirs('dist')
for f in TOP_FILES: shutil.copy2(f, 'dist/' + f)
for d in DIRS:
    if os.path.isdir(d):
        shutil.copytree(d, f'dist/{d}', ignore=shutil.ignore_patterns('_incoming', '*.md', '.gitkeep', '.DS_Store'))

n, total, big = 0, 0, []
for dp, _, fs in os.walk('dist'):
    for f in fs:
        sz = os.path.getsize(os.path.join(dp, f)); n += 1; total += sz
        if sz > 25 * 1024 * 1024: big.append(f)
print(f'dist/ ready: {n} files, {total / 1024 / 1024:.1f} MB')
if n > 1000: print('WARNING: Cloudflare drag-and-drop accepts at most 1,000 files; use the GitHub method instead.')
if big: print('WARNING: files over 25 MB are rejected:', big)
if '--zip' in sys.argv:
    shutil.make_archive('dist', 'zip', 'dist'); print('dist.zip created')
