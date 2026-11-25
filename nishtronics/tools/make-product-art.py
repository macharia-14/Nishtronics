#!/usr/bin/env python3
"""
Draws a clean vector illustration for every product in data/products.json and writes it to
images/products/<id>.svg. These stand in until you have real photos: a real photo named
images/products/<id>.webp (see tools/prepare-images.py) always wins over the drawing.

  python tools/make-product-art.py            # redraw all
  python tools/make-product-art.py kw-6x9-kfc1669s   # redraw one

Product type, size and brand are read from the product (category, name, brand), so new
products get a sensible drawing automatically. Brand names appear as plain text only.
"""
import json, os, re, sys, math

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)

ACCENT = {
    'Kenwood': '#22c1c3', 'Pioneer': '#3b82f6', 'Nakamichi': '#d4af37', 'Sundown Audio': '#f97316',
    'Kicker': '#ef4444', 'Rockford Fosgate': '#facc15', 'Taramps': '#22c55e', 'Nishtronics': '#e8c96a',
    'Concox': '#60a5fa', 'Teltonika': '#38bdf8',
}

DEFS = """
<defs>
  <radialGradient id="cone" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#4a4e5a"/><stop offset=".55" stop-color="#262932"/><stop offset="1" stop-color="#101116"/></radialGradient>
  <radialGradient id="cap" cx="38%" cy="35%" r="70%"><stop offset="0" stop-color="#f4f4f6"/><stop offset=".45" stop-color="#b9bcc6"/><stop offset="1" stop-color="#5c606c"/></radialGradient>
  <radialGradient id="capdark" cx="38%" cy="35%" r="70%"><stop offset="0" stop-color="#5a5e6b"/><stop offset=".5" stop-color="#2b2e37"/><stop offset="1" stop-color="#14151a"/></radialGradient>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b3e49"/><stop offset=".5" stop-color="#1b1c22"/><stop offset="1" stop-color="#0d0d11"/></linearGradient>
  <linearGradient id="rubber" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a2c33"/><stop offset="1" stop-color="#08080b"/></linearGradient>
  <linearGradient id="chassis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d3039"/><stop offset=".5" stop-color="#17181d"/><stop offset="1" stop-color="#0b0b0e"/></linearGradient>
  <linearGradient id="fin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0c0c10"/><stop offset=".45" stop-color="#454956"/><stop offset=".55" stop-color="#5a5f6d"/><stop offset="1" stop-color="#0c0c10"/></linearGradient>
  <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16243f"/><stop offset="1" stop-color="#0a0f1d"/></linearGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8b6f4e"/><stop offset="1" stop-color="#5b472f"/></linearGradient>
  <linearGradient id="woodside" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6d563c"/><stop offset="1" stop-color="#47372a"/></linearGradient>
  <linearGradient id="woodtop" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a98a63"/><stop offset="1" stop-color="#8b6f4e"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>"""

def wrap(body, label=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="{label}">{DEFS}'
            f'<ellipse cx="300" cy="528" rx="190" ry="20" fill="#000" opacity=".28" filter="url(#blur)"/>{body}</svg>')

def spec_num(text, pat, default):
    m = re.search(pat, text, re.I)
    return float(m.group(1)) if m else default

# ───────────────────────── drawers ─────────────────────────
def speaker(rx, ry, accent, coax=True):
    cx, cy = 300, 285
    b = ''
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#frame)" stroke="#5a5f6e" stroke-width="2"/>'
    for ang in (45, 135, 225, 315):
        x = cx + math.cos(math.radians(ang)) * rx * .88
        y = cy + math.sin(math.radians(ang)) * ry * .88
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{min(rx,ry)*.055:.1f}" fill="#06060a" stroke="#454a58" stroke-width="2"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.8:.1f}" ry="{ry*.8:.1f}" fill="url(#rubber)" stroke="#33363f" stroke-width="3"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.7:.1f}" ry="{ry*.7:.1f}" fill="none" stroke="{accent}" stroke-width="3" opacity=".85"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.66:.1f}" ry="{ry*.66:.1f}" fill="url(#cone)"/>'
    for k in (.58, .5, .42, .34):
        b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*k:.1f}" ry="{ry*k:.1f}" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="2"/>'
    if coax:
        b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.21:.1f}" ry="{ry*.21:.1f}" fill="url(#cap)" stroke="#2a2d36" stroke-width="3"/>'
        b += f'<ellipse cx="{cx-rx*.05:.1f}" cy="{cy-ry*.06:.1f}" rx="{rx*.08:.1f}" ry="{ry*.05:.1f}" fill="#fff" opacity=".7"/>'
    b += f'<path d="M{cx-rx*.9:.0f} {cy-ry*.25:.0f} A{rx*.95:.0f} {ry*.95:.0f} 0 0 1 {cx-rx*.25:.0f} {cy-ry*.9:.0f}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="6" stroke-linecap="round"/>'
    return b

def sub(size, accent, powered=False):
    R = {8: 150, 10: 175, 12: 200, 15: 225}.get(int(size), 190)
    cx, cy = 300, 285
    s = R * 1.06
    b = f'<rect x="{cx-s}" y="{cy-s}" width="{2*s}" height="{2*s}" rx="{s*.2:.0f}" fill="url(#frame)" stroke="#5a5f6e" stroke-width="2"/>'
    for sx in (-1, 1):
        for sy in (-1, 1):
            b += f'<circle cx="{cx+sx*s*.82:.0f}" cy="{cy+sy*s*.82:.0f}" r="{s*.04:.0f}" fill="#06060a" stroke="#454a58" stroke-width="2"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.97:.0f}" fill="#0a0a0d" stroke="#2c2f38" stroke-width="3"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.9:.0f}" fill="url(#rubber)"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.78:.0f}" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="5"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.72:.0f}" fill="none" stroke="{accent}" stroke-width="4" opacity=".9"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.68:.0f}" fill="url(#cone)"/>'
    for k in (.6, .52, .44):
        b += f'<circle cx="{cx}" cy="{cy}" r="{R*k:.0f}" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="2"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.3:.0f}" fill="url(#capdark)" stroke="#555a68" stroke-width="3"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R*.22:.0f}" fill="none" stroke="{accent}" stroke-width="3" opacity=".8"/>'
    b += f'<ellipse cx="{cx-R*.08:.0f}" cy="{cy-R*.1:.0f}" rx="{R*.1:.0f}" ry="{R*.06:.0f}" fill="#fff" opacity=".22"/>'
    b += f'<path d="M{cx-R*.85:.0f} {cy-R*.3:.0f} A{R*.9:.0f} {R*.9:.0f} 0 0 1 {cx-R*.3:.0f} {cy-R*.85:.0f}" fill="none" stroke="#fff" stroke-opacity=".15" stroke-width="7" stroke-linecap="round"/>'
    if powered:
        b += f'<rect x="{cx+s*.2:.0f}" y="{cy+s*.78:.0f}" width="{s*.7:.0f}" height="26" rx="6" fill="#0a0a0d" stroke="{accent}" stroke-width="2"/><text x="{cx+s*.55:.0f}" y="{cy+s*.78+18:.0f}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="14" fill="{accent}">POWERED</text>'
    return b

def amp(channels, accent, brand, model):
    W = {1: 400, 2: 440, 4: 500, 5: 520}.get(channels, 480)
    H = 250
    x0, y0 = 300 - W / 2, 285 - H / 2
    b = f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" rx="22" fill="url(#chassis)" stroke="#555a68" stroke-width="2"/>'
    fins = int((W - 140) / 14)
    for i in range(fins):
        x = x0 + 70 + i * 14
        b += f'<rect x="{x}" y="{y0+16}" width="9" height="{H-32}" rx="3" fill="url(#fin)"/>'
    b += f'<rect x="{300-110}" y="{285-48}" width="220" height="96" rx="14" fill="#0b0c10" stroke="{accent}" stroke-width="2" opacity=".96"/>'
    b += f'<text x="300" y="{285-6}" text-anchor="middle" font-family="Arial Black, Arial" font-weight="900" font-size="26" fill="#fff" letter-spacing="2">{brand.upper().replace('FOSGATE','').strip()[:11]}</text>'
    b += f'<text x="300" y="{285+22}" text-anchor="middle" font-family="Arial" font-weight="600" font-size="15" fill="{accent}" letter-spacing="3">{model[:14].upper()}</text>'
    b += f'<circle cx="{300+88}" cy="{285-30}" r="5" fill="#22c55e"/><circle cx="{300+88}" cy="{285-30}" r="11" fill="#22c55e" opacity=".25"/>'
    for sx in (x0 + 24, x0 + W - 24):
        for k in range(3 if channels > 1 else 2):
            b += f'<circle cx="{sx}" cy="{y0+50+k*52}" r="14" fill="#c9a84c" stroke="#6b5520" stroke-width="3"/><circle cx="{sx}" cy="{y0+50+k*52}" r="5" fill="#1b150a"/>'
    for i, c in enumerate(('#e5e7eb', '#ef4444')):
        b += f'<circle cx="{x0+W-70-i*30}" cy="{y0+H-26}" r="9" fill="{c}" stroke="#222" stroke-width="2"/><circle cx="{x0+W-70-i*30}" cy="{y0+H-26}" r="3.5" fill="#111"/>'
    b += f'<circle cx="{x0+70}" cy="{y0+H-26}" r="13" fill="url(#capdark)" stroke="#6b707e" stroke-width="2"/><line x1="{x0+70}" y1="{y0+H-26}" x2="{x0+70}" y2="{y0+H-37}" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>'
    return b

def headunit(kind, accent, brand):
    if kind == 'din':
        b = '<rect x="60" y="215" width="480" height="150" rx="16" fill="url(#chassis)" stroke="#555a68" stroke-width="2"/>'
        b += '<rect x="92" y="240" width="190" height="56" rx="8" fill="#06141b" stroke="#2c4a57" stroke-width="2"/>'
        b += f'<text x="187" y="278" text-anchor="middle" font-family="Courier New, monospace" font-weight="700" font-size="30" fill="{accent}">12:00 FM</text>'
        b += f'<circle cx="452" cy="290" r="48" fill="url(#capdark)" stroke="#7b8090" stroke-width="3"/><circle cx="452" cy="290" r="36" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="2"/><line x1="452" y1="290" x2="452" y2="250" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>'
        for i in range(6):
            b += f'<rect x="{96+i*32}" y="318" width="24" height="16" rx="4" fill="#23252d" stroke="#3d414d"/>'
        b += f'<rect x="304" y="326" width="40" height="22" rx="5" fill="#0a0a0d" stroke="#454a58"/>'
        b += f'<text x="104" y="360" font-family="Arial Black, Arial" font-weight="900" font-size="12" fill="#8b8f9c" letter-spacing="3">{brand.upper()}</text>'
        return b
    W = 540 if kind == 'wide' else 500
    H = 330 if kind == 'wide' else 340
    x0, y0 = 300 - W / 2, 285 - H / 2
    b = f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" rx="22" fill="url(#chassis)" stroke="#555a68" stroke-width="2"/>'
    b += f'<rect x="{x0+60}" y="{y0+18}" width="{W-80}" height="{H-36}" rx="12" fill="url(#screen)" stroke="#0a0a0d" stroke-width="3"/>'
    b += f'<rect x="{x0+60}" y="{y0+18}" width="{W-80}" height="{(H-36)*.5}" rx="12" fill="url(#glass)"/>'
    tiles = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4']
    gw = W - 80
    for i, c in enumerate(tiles):
        tx = x0 + 60 + 26 + (i % 3) * (gw - 52) / 3
        ty = y0 + 18 + 52 + (i // 3) * 88
        b += f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{(gw-90)/3:.0f}" height="68" rx="14" fill="{c}" opacity=".85"/>'
    b += f'<text x="{x0+60+26}" y="{y0+18+36}" font-family="Arial" font-weight="700" font-size="20" fill="#e5e7eb">12:00</text>'
    b += f'<rect x="{x0+60+16}" y="{y0+H-18-44}" width="{gw-32}" height="26" rx="13" fill="#fff" opacity=".08"/>'
    b += f'<circle cx="{x0+30}" cy="{y0+90}" r="22" fill="url(#capdark)" stroke="#7b8090" stroke-width="2"/><line x1="{x0+30}" y1="{y0+90}" x2="{x0+30}" y2="{y0+72}" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>'
    b += f'<circle cx="{x0+30}" cy="{y0+170}" r="14" fill="#23252d" stroke="#454a58"/><circle cx="{x0+30}" cy="{y0+215}" r="14" fill="#23252d" stroke="#454a58"/>'
    return b

def tracker(accent, light=False):
    body = '#f4f5f7' if light else '#15161b'
    b = f'<path d="M150 410 C 120 450, 190 500, 230 470" fill="none" stroke="#111" stroke-width="10" stroke-linecap="round"/><rect x="214" y="452" width="46" height="30" rx="6" fill="#222" stroke="#555"/>'
    b += f'<rect x="150" y="215" width="300" height="190" rx="26" fill="{body}" stroke="#6b707e" stroke-width="3"/>'
    b += f'<rect x="150" y="215" width="300" height="80" rx="26" fill="url(#glass)"/>'
    b += f'<rect x="178" y="330" width="244" height="46" rx="10" fill="{accent}" opacity=".9"/>'
    b += f'<text x="300" y="362" text-anchor="middle" font-family="Arial Black, Arial" font-weight="900" font-size="26" fill="#0a0a0d" letter-spacing="6">GPS</text>'
    b += f'<circle cx="190" cy="252" r="9" fill="{accent}"/><circle cx="190" cy="252" r="18" fill="{accent}" opacity=".25"/>'
    for i, r in enumerate((70, 105, 140)):
        b += f'<path d="M{300-r} 190 A{r} {r} 0 0 1 {300+r} 190" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round" opacity="{.8-i*.22:.2f}"/>'
    return b

def wiring(awg, accent):
    t = 24 if awg <= 4 else 15
    b = ''
    for cx, cy, col, dark in ((235, 330, '#ef4444', '#7f1d1d'), (365, 340, '#26262c', '#0a0a0c')):
        for i in range(5):
            b += f'<ellipse cx="{cx}" cy="{cy-i*7}" rx="{110-i*4}" ry="{78-i*3}" fill="none" stroke="{dark}" stroke-width="{t+4}"/>'
            b += f'<ellipse cx="{cx}" cy="{cy-i*7}" rx="{110-i*4}" ry="{78-i*3}" fill="none" stroke="{col}" stroke-width="{t}"/>'
        b += f'<ellipse cx="{cx-30}" cy="{cy-40}" rx="60" ry="30" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="5" transform="rotate(-12 {cx} {cy})"/>'
    b += f'<rect x="258" y="215" width="84" height="46" rx="10" fill="#1c1d22" stroke="#555a68" stroke-width="2"/><rect x="274" y="226" width="52" height="24" rx="5" fill="#f59e0b" opacity=".9"/>'
    b += f'<text x="300" y="244" text-anchor="middle" font-family="Arial Black, Arial" font-weight="900" font-size="14" fill="#1b1204">{awg} AWG</text>'
    for x in (150, 450):
        b += f'<circle cx="{x}" cy="440" r="15" fill="#c9a84c" stroke="#6b5520" stroke-width="3"/><circle cx="{x}" cy="440" r="5" fill="#1b150a"/>'
    return b

def box(kind, accent, size=12):
    # isometric cube: left face (front), right face (side), top face
    fx0, fy0, fw, fh = 130, 260, 270, 260
    dx, dy = 105, -62
    carpet = kind == 'fibreglass'
    b = ''
    if kind == 'fibreglass':
        b += '<path d="M120 330 C 120 230, 230 180, 330 190 C 440 200, 500 280, 480 390 C 465 470, 380 520, 290 515 C 190 510, 120 450, 120 330 Z" fill="#14151a" stroke="#555a68" stroke-width="3"/>'
        b += '<path d="M150 300 C 170 240, 250 210, 330 215" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="8" stroke-linecap="round"/>'
        cx, cy, R = 300, 360, 118
    else:
        b += f'<polygon points="{fx0},{fy0} {fx0+dx},{fy0+dy} {fx0+fw+dx},{fy0+dy} {fx0+fw},{fy0}" fill="url(#woodtop)" stroke="#3a2d1f" stroke-width="2"/>'
        b += f'<polygon points="{fx0+fw},{fy0} {fx0+fw+dx},{fy0+dy} {fx0+fw+dx},{fy0+dy+fh} {fx0+fw},{fy0+fh}" fill="url(#woodside)" stroke="#3a2d1f" stroke-width="2"/>'
        b += f'<rect x="{fx0}" y="{fy0}" width="{fw}" height="{fh}" fill="url(#wood)" stroke="#3a2d1f" stroke-width="2"/>'
        for i in range(6):
            b += f'<line x1="{fx0}" y1="{fy0+25+i*42}" x2="{fx0+fw}" y2="{fy0+22+i*42}" stroke="#000" stroke-opacity=".08" stroke-width="3"/>'
        cx, cy, R = fx0 + fw / 2 - (30 if kind == 'ported' else 0), fy0 + fh / 2 + 6, 98
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#0a0a0d" stroke="#555a68" stroke-width="4"/><circle cx="{cx}" cy="{cy}" r="{R*.86:.0f}" fill="url(#rubber)"/><circle cx="{cx}" cy="{cy}" r="{R*.7:.0f}" fill="none" stroke="{accent}" stroke-width="3" opacity=".9"/><circle cx="{cx}" cy="{cy}" r="{R*.64:.0f}" fill="url(#cone)"/><circle cx="{cx}" cy="{cy}" r="{R*.28:.0f}" fill="url(#capdark)" stroke="#555a68" stroke-width="2"/>'
    if kind == 'ported':
        b += f'<rect x="{fx0+fw-84}" y="{fy0+fh-88}" width="64" height="64" rx="10" fill="#050507" stroke="#555a68" stroke-width="3"/><circle cx="{fx0+fw-52}" cy="{fy0+fh-56}" r="22" fill="none" stroke="#2c2f38" stroke-width="3"/>'
    return b

# ───────────────────────── dispatcher ─────────────────────────
def draw(p):
    name, cat, brand = p['name'], p['category'], p['brand']
    accent = ACCENT.get(brand, '#e8c96a')
    low = name.lower()
    size = spec_num(name, r'(\d+(?:\.\d+)?)\s*["”]', 0)
    if cat == 'secondhand':
        cat = 'headunits' if 'head' in low else 'subwoofers'
    if cat == 'speakers':
        if '6x9' in low:
            return speaker(255, 168, accent, coax=('3-way' in low or '3 way' in low) or True)
        return speaker(215, 215, accent)
    if cat == 'subwoofers':
        return sub(size or 12, accent, powered='powered' in low)
    if cat == 'amplifiers':
        ch = 1 if 'mono' in low or '.1' in low else (4 if '4-channel' in low or 'x4' in low else 2)
        model = re.sub(r'^(Kenwood|Pioneer|Nakamichi|Taramps|Rockford Fosgate)\s+', '', name)
        model = re.sub(r'\s+(4-Channel|Mono|Amplifier|Amp)\b.*$', '', model, flags=re.I)
        return amp(ch, accent, brand, model)
    if cat == 'headunits':
        if 'screen' in low or 'ddx' in low or 'dmh' in low or 'android' in low:
            return headunit('wide' if ('9"' in name or 'android' in low) else 'screen', accent, brand)
        return headunit('din', accent, brand)
    if cat == 'trackers':
        return tracker(accent, light='concox' in low)
    if cat == 'accessories':
        if 'wiring' in low:
            return wiring(int(spec_num(name, r'(\d+)\s*AWG', 4)), accent)
        if 'fibre' in low or 'fiber' in low:
            return box('fibreglass', accent, size or 15)
        if 'ported' in low:
            return box('ported', accent, size or 12)
        return box('sealed', accent, size or 12)
    return sub(12, accent)

def main():
    products = json.load(open('data/products.json', encoding='utf-8'))
    only = set(sys.argv[1:])
    os.makedirs('images/products', exist_ok=True)
    n = 0
    for p in products:
        if only and p['id'] not in only:
            continue
        svg = wrap(draw(p), p['name'].replace('"', '&quot;'))
        open(f"images/products/{p['id']}.svg", 'w', encoding='utf-8').write(svg)
        n += 1
    print(f'wrote {n} illustrations to images/products/')

if __name__ == '__main__':
    main()
