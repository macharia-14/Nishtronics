#!/usr/bin/env python3
"""
Single source of truth for the site menu. Edit LINKS below, then run:

    python tools/sync-nav.py

It rewrites the menu (desktop bar + mobile drawer) in every top-level page, marks the current page,
keeps your phone number as it is, and makes sure the footer links to every page in LINKS.
Run tools/build-blog.py afterwards so the blog pages pick up the new menu.
"""
import glob, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)

# (file, label, icon id from js/icons.js)
LINKS = [('index.html', 'Home', 'home'), ('products.html', 'Products', 'package'), ('services.html', 'Services', 'tool'),
         ('gallery.html', 'Gallery', 'image'), ('blog.html', 'Blog', 'book-open'), ('about.html', 'About', 'info'),
         ('contact.html', 'Contact', 'message-circle')]

def svg(name, cls=''):
    return f'<svg class="i{(" " + cls) if cls else ""}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'

NAV_RE = re.compile(r'<header class="nav" id="nav">.*?</aside>', re.S)

def nav_html(page, wa, tel, tel_text):
    cur = lambda h: ' aria-current="page"' if h == page else ''
    links = ''.join(f'<a href="{h}"{cur(h)}>{l}</a>' for h, l, _ in LINKS)
    mm = ''.join(f'<a href="{h}"{cur(h)}>{svg(i)}{l}</a>' for h, l, i in LINKS)
    theme = lambda extra='': (f'<button class="theme-toggle nav-icon" {extra}data-theme-toggle aria-label="Switch to light theme" '
                              f'title="Light / dark theme">{svg("sun", "i-sun")}{svg("moon", "i-moon")}</button>')
    brand = '<span class="nav-brand"><b>NISHTRONICS</b><small>SOUNDLABS</small></span>'
    return f'''<header class="nav" id="nav">
  <div class="nav-inner">
    <a href="index.html" class="nav-logo" aria-label="Nishtronics Soundlabs, home"><span class="lm">{svg("wave")}</span>{brand}</a>
    <nav class="nav-links" id="navLinks" aria-label="Main">
      {links}
      <span class="nav-fader" aria-hidden="true"></span>
    </nav>
    <div class="nav-actions">
      <a class="nav-phone" href="tel:+{tel}">{svg("phone")}<span>{tel_text}</span></a>
      {theme('id="themeToggle" ')}
      <button class="nav-icon nav-cart" id="openCart" aria-label="Open cart">{svg("cart")}<span class="cart-pip zero" id="cartPip">0</span></button>
      <a class="nav-cta" href="booking.html"{cur("booking.html")}>{svg("calendar")}<span>Book a job</span></a>
      <button class="nav-icon nav-burger" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">{svg("menu")}</button>
    </div>
  </div>
</header>
<div class="nav-scrim" id="navScrim"></div>
<aside class="mobile-menu" id="mobileMenu" aria-label="Menu">
  <div class="mm-head">
    {brand}
    {theme()}
    <button class="nav-icon mm-close" aria-label="Close menu">{svg("x")}</button>
  </div>
  <nav class="mm-links" aria-label="Mobile">
    {mm}
  </nav>
  <div class="mm-foot">
    <a class="btn btn-gold" href="booking.html"{cur("booking.html")}>{svg("calendar")}Book a job</a>
    <a class="btn btn-wa" href="https://wa.me/{wa}" target="_blank" rel="noopener">{svg("whatsapp")}WhatsApp us</a>
    <a class="mm-phone" href="tel:+{tel}">{svg("phone")}<span>{tel_text}</span></a>
  </div>
</aside>'''

def sync_footer(s):
    """Footer 'Pages' list: add any LINKS entry that is missing, after the page before it."""
    for idx, (h, l, _) in enumerate(LINKS):
        if f'<li><a href="{h}">' in s or idx == 0: continue
        prev = LINKS[idx - 1][0]
        m = re.search(rf'<li><a href="{re.escape(prev)}">[^<]*</a></li>', s)
        if m: s = s[:m.end()] + f'<li><a href="{h}">{l}</a></li>' + s[m.end():]
    return s

changed = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    m = NAV_RE.search(s)
    if not m: continue
    old = m.group(0)
    wa = re.search(r'wa\.me/(\d+)', old).group(1)
    tel = re.search(r'class="nav-phone" href="tel:\+(\d+)"', old).group(1)
    tel_text = re.search(r'class="nav-phone"[^>]*>.*?<span>([^<]*)</span>', old, re.S).group(1)
    s2 = s[:m.start()] + nav_html(f, wa, tel, tel_text) + s[m.end():]
    s2 = sync_footer(s2)
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); changed += 1
print(f'menu synced in {changed} pages')
