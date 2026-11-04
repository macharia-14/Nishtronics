#!/usr/bin/env python3
"""
Set the real WhatsApp/phone number (and optionally social links) everywhere at once.

  python tools/set-contact.py 254712345678
  python tools/set-contact.py 254712345678 --instagram https://instagram.com/yourshop --facebook https://facebook.com/yourshop

Safe to re-run. Run it from the project root or from tools/.
"""
import argparse, glob, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('number', help='Kenyan number in international format, digits only, e.g. 254712345678')
ap.add_argument('--instagram'); ap.add_argument('--facebook')
a = ap.parse_args()

if not re.fullmatch(r'254[17]\d{8}', a.number):
    sys.exit('Number must look like 254712345678 (254 + 9 digits starting 7 or 1, no + or spaces).')

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(root)
n = a.number
display = f'+{n[:3]} {n[3:6]} {n[6:9]} {n[9:]}'

files = glob.glob('*.html') + glob.glob('*.snippet') + glob.glob('js/*.js')
changed = {}
for f in files:
    s = o = open(f, encoding='utf-8').read()
    s = re.sub(r'wa\.me/\d+', f'wa.me/{n}', s)
    s = re.sub(r'(<a href="tel:)\+\d+("[^>]*>)[^<]*(</a>)', rf'\g<1>+{n}\2{display}\3', s)
    if a.instagram: s = re.sub(r'href="https?://(www\.)?instagram\.com[^"]*"', f'href="{a.instagram}"', s)
    if a.facebook:  s = re.sub(r'href="https?://(www\.)?facebook\.com[^"]*"',  f'href="{a.facebook}"',  s)
    if s != o:
        open(f, 'w', encoding='utf-8').write(s); changed[f] = True

left = [f for f in files if '254700000000' in open(f, encoding='utf-8').read()]
print(f'Updated {len(changed)} files. Number: {display}')
if left: print('Placeholder number still present in:', ', '.join(left))
