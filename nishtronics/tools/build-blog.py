#!/usr/bin/env python3
"""
Builds the blog from the markdown files in content/blog/.

  python tools/build-blog.py                          # rebuild blog.html, blog/*.html, home page block
  python tools/build-blog.py --site https://yourdomain.co.ke   # also writes sitemap.xml, robots.txt, feed.xml
                                                               # and adds canonical / social-share tags

Every post is a file like content/blog/my-new-post.md:

    ---
    title: My new post
    date: 2026-11-20
    category: Guides            (any word; becomes a filter on the blog page)
    excerpt: One or two sentences shown on cards and in search results.
    cover: images/blog/my-new-post.webp     (optional; a default cover is used if omitted)
    ---
    Body in simple markdown: ## headings, **bold**, *italic*, [links](page.html),
    - bullet lists, 1. numbered lists, > quotes, | tables |, and --- rules.

Use {{wa}} in a link to insert your WhatsApp number: [message us](https://wa.me/{{wa}}).
Link to other pages by file name (products.html, booking.html) or to another post by its
file name without .md (sealed-vs-ported-subwoofer.html); paths are fixed up for you.

The page chrome (menu, footer, scripts) is copied from about.html, so run tools/sync-nav.py and
tools/set-contact.py first if you changed the menu or your phone number, then rebuild.
"""
import argparse, datetime, glob, hashlib, html, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)

ap = argparse.ArgumentParser()
ap.add_argument('--site', help='public site address, e.g. https://nishtronics.co.ke (no trailing slash)')
args = ap.parse_args()
SITE = (args.site or '').rstrip('/')

# ───────────────────────── helpers ─────────────────────────
def esc(s): return html.escape(s, quote=True)

def read(p): return open(p, encoding='utf-8').read()

def fmt_date(d):
    return f"{d.day} {d.strftime('%b %Y')}"

def parse_post(path):
    raw = read(path).replace('\r\n', '\n')
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m:
        sys.exit(f'{path}: missing front matter (--- ... ---) at the top')
    meta = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1); meta[k.strip().lower()] = v.strip()
    for need in ('title', 'date', 'excerpt'):
        if need not in meta: sys.exit(f'{path}: front matter needs "{need}"')
    slug = os.path.splitext(os.path.basename(path))[0]
    body = m.group(2).strip()
    words = len(re.findall(r'\w+', re.sub(r'[#*>|`\[\]\(\)-]', ' ', body)))
    return dict(slug=slug, title=meta['title'], date=datetime.date.fromisoformat(meta['date']),
                category=meta.get('category', 'Guides'), excerpt=meta['excerpt'], cover=meta.get('cover', ''),
                body=body, mins=max(1, math.ceil(words / 200)))

posts = sorted((parse_post(p) for p in glob.glob('content/blog/*.md')), key=lambda p: p['date'], reverse=True)
if not posts: sys.exit('no posts found in content/blog/')
SLUGS = {p['slug'] for p in posts}

for p in posts:
    if not p['cover']:
        n = int(hashlib.md5(p['slug'].encode()).hexdigest(), 16) % 4 + 1
        p['cover'] = f'images/blog/default-{n}.webp'

# ───────────────────────── page chrome from about.html ─────────────────────────
about = read('about.html')
NAV = re.search(r'<header class="nav" id="nav">.*?</aside>', about, re.S).group(0).replace(' aria-current="page"', '')
FOOT = re.search(r'<footer class="footer">.*?(?=<script src="js/firebase\.js">)', about, re.S).group(0)
WA = re.search(r'wa\.me/(\d+)', NAV).group(1)

def prefix(markup, base):
    """Make root-relative asset/page links work from blog/ (base='../')."""
    if not base: return markup
    return re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:|\.\./)([^"]+)"', lambda m: f'{m.group(1)}="{base}{m.group(2)}"', markup)

def nav_for(base):
    n = NAV.replace('<a href="blog.html"', '<a aria-current="page" href="blog.html"')
    return prefix(n, base)

def fix_href(href, in_post):
    if re.match(r'^(https?:|mailto:|tel:|#|/)', href): return href
    name, _, frag = href.partition('#')
    stem = name[:-5] if name.endswith('.html') else name
    frag = ('#' + frag) if frag else ''
    if stem in SLUGS: return (stem + '.html' if in_post else 'blog/' + stem + '.html') + frag
    return ('../' if in_post else '') + name + frag

# ───────────────────────── markdown ─────────────────────────
def inline(s, in_post):
    s = esc(s)
    codes = []
    def keep(m): codes.append(m.group(1)); return f'\x00{len(codes)-1}\x00'
    s = re.sub(r'`([^`]+)`', keep, s)
    def link(m):
        href = fix_href(m.group(2).replace('&amp;', '&'), in_post)
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        return f'<a href="{esc(href)}"{ext}>{m.group(1)}</a>'
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])', r'<em>\1</em>', s)
    return re.sub(r'\x00(\d+)\x00', lambda m: f'<code>{codes[int(m.group(1))]}</code>', s)

def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

def md(body, in_post):
    body = body.replace('{{wa}}', WA)
    lines = body.split('\n'); out = []; i = 0
    block_start = lambda l: re.match(r'^(#{2,3} |>|\s*[-*] |\s*\d+\. |\||---$)', l)
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('## ') or l.startswith('### '):
            lvl = 2 if l.startswith('## ') else 3; t = l[lvl + 1:].strip()
            out.append(f'<h{lvl} id="{slugify(t)}">{inline(t, in_post)}</h{lvl}>'); i += 1
        elif l.strip() == '---':
            out.append('<hr>'); i += 1
        elif l.startswith('>'):
            q = []
            while i < len(lines) and lines[i].startswith('>'): q.append(lines[i].lstrip('> ').rstrip()); i += 1
            out.append('<blockquote><p>' + inline(' '.join(q), in_post) + '</p></blockquote>')
        elif re.match(r'^\s*[-*] ', l):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*] ', lines[i]): items.append(re.sub(r'^\s*[-*] ', '', lines[i])); i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x, in_post)}</li>' for x in items) + '</ul>')
        elif re.match(r'^\s*\d+\. ', l):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\. ', lines[i]): items.append(re.sub(r'^\s*\d+\. ', '', lines[i])); i += 1
            out.append('<ol>' + ''.join(f'<li>{inline(x, in_post)}</li>' for x in items) + '</ol>')
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'): rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            head, rest = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            t = '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th>{inline(c, in_post)}</th>' for c in head) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline(c, in_post)}</td>' for c in r) + '</tr>' for r in rest) + '</tbody></table></div>'
            out.append(t)
        else:
            para = [l.strip()]; i += 1
            while i < len(lines) and lines[i].strip() and not block_start(lines[i]): para.append(lines[i].strip()); i += 1
            out.append('<p>' + inline(' '.join(para), in_post) + '</p>')
    return '\n'.join(out)

# ───────────────────────── components ─────────────────────────
def svg(name): return f'<svg class="i" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'

def card(p, base, cls='post-card'):
    href = (base + 'blog/' if not base else '') + p['slug'] + '.html'
    cover = base + p['cover']
    return (f'<a class="{cls} reveal" href="{href}" data-cat="{esc(p["category"])}">'
            f'<div class="post-cover"><img src="{cover}" alt="" loading="lazy" width="1200" height="630"/></div>'
            f'<div class="post-body"><span class="post-cat">{esc(p["category"])}</span><h3>{esc(p["title"])}</h3>'
            f'<p>{esc(p["excerpt"])}</p>'
            f'<div class="post-meta"><span>{fmt_date(p["date"])}</span><span>{p["mins"]} min read</span></div></div></a>')

def head(title, desc, base, extra=''):
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>\n'
            f'<meta name="description" content="{esc(desc)}"/>\n<title>{esc(title)}</title>\n{extra}'
            f'<link rel="stylesheet" href="{base}css/style.css"/>\n</head>\n<body>\n<script src="{base}js/icons.js"></script>\n\n')

def tail(base):
    return (f'\n{prefix(FOOT, base)}<script src="{base}js/firebase.js"></script>\n<script src="{base}js/main.js"></script>\n</body>\n</html>\n')

def social(title, desc, url_path, cover):
    if not SITE: return ''
    u = f'{SITE}/{url_path}'
    return (f'<link rel="canonical" href="{u}"/>\n<meta property="og:type" content="article"/>\n<meta property="og:title" content="{esc(title)}"/>\n'
            f'<meta property="og:description" content="{esc(desc)}"/>\n<meta property="og:url" content="{u}"/>\n'
            f'<meta property="og:image" content="{SITE}/{cover}"/>\n<meta name="twitter:card" content="summary_large_image"/>\n')

HERO_BG = {'Guides': 'waves', 'Buying advice': 'bokeh', 'How-to': 'cables'}

# ───────────────────────── blog index ─────────────────────────
def build_index():
    feat, rest = posts[0], posts[1:]
    cats = sorted({p['category'] for p in posts})
    chips = '<button class="chip active" data-cat="all">All</button>' + ''.join(f'<button class="chip" data-cat="{esc(c)}">{esc(c)}</button>' for c in cats)
    fcard = (f'<a class="post-feature reveal" href="blog/{feat["slug"]}.html"><div class="post-cover"><img src="{feat["cover"]}" alt="" width="1200" height="630"/></div>'
             f'<div class="post-body"><span class="post-cat">Latest &middot; {esc(feat["category"])}</span><h2>{esc(feat["title"])}</h2><p>{esc(feat["excerpt"])}</p>'
             f'<div class="post-meta"><span>{fmt_date(feat["date"])}</span><span>{feat["mins"]} min read</span></div>'
             f'<span class="post-more">Read the article {svg("arrow-right")}</span></div></a>')
    page = head('Blog | Nishtronics Soundlabs', 'Plain-English guides on car audio, home theatre and vehicle tracking from the Nishtronics Soundlabs team in Nairobi.', '',
                social('Sound Advice | Nishtronics Soundlabs', 'Plain-English guides on car audio, home theatre and vehicle tracking.', 'blog.html', feat['cover'])) + nav_for('')
    page += f'''
<section class="page-hero">
  <img class="page-hero-bg" src="images/bg/groove.webp" alt=""/>
  <div class="page-hero-overlay"></div>
  <div class="page-hero-inner container">
    <span class="page-kicker">The Blog</span>
    <h1>Sound Advice</h1>
    <p style="color:var(--t2);margin-top:.875rem;max-width:560px;margin-left:auto;margin-right:auto;font-size:.95rem;line-height:1.7;">
      Plain-English guides on car audio, home theatre and tracking, from the people who install it.
    </p>
  </div>
</section>

<section class="cut-top" style="background:var(--ink);padding:6rem 0 7rem;">
  <div class="container">
    {fcard}
    <div class="blog-tools reveal">
      <div class="chips" id="blogChips" role="group" aria-label="Filter articles">{chips}</div>
      <span class="results-info" id="blogCount">{len(posts)} articles</span>
    </div>
    <div class="blog-grid" id="blogGrid">
      {''.join(card(p, '') for p in rest)}
    </div>
    <div class="post-cta reveal" style="margin-top:4.5rem;">
      <div>
        <h3>Have a question we have not answered?</h3>
        <p>Send us the make and model of your car and what you want to improve. We reply on WhatsApp, usually within the hour.</p>
      </div>
      <div class="post-cta-btns">
        <a href="https://wa.me/{WA}" class="btn btn-wa btn-lg" target="_blank" rel="noopener">{svg("whatsapp")}WhatsApp us</a>
        <a href="booking.html" class="btn btn-gold btn-lg">{svg("calendar")}Book a job</a>
      </div>
    </div>
  </div>
</section>

<script>
(function () {{
  var chips = document.querySelectorAll('#blogChips .chip');
  var cards = document.querySelectorAll('#blogGrid .post-card');
  var feat = document.querySelector('.post-feature');
  var count = document.getElementById('blogCount');
  chips.forEach(function (c) {{
    c.addEventListener('click', function () {{
      chips.forEach(function (x) {{ x.classList.toggle('active', x === c); }});
      var cat = c.dataset.cat, shown = 0;
      cards.forEach(function (card) {{
        var ok = cat === 'all' || card.dataset.cat === cat;
        card.hidden = !ok; if (ok) shown++;
      }});
      if (feat) feat.hidden = cat !== 'all';
      var n = cat === 'all' ? shown + 1 : shown;
      count.textContent = n + (n === 1 ? ' article' : ' articles');
    }});
  }});
}})();
</script>
''' + tail('')
    open('blog.html', 'w', encoding='utf-8').write(page)

# ───────────────────────── post pages ─────────────────────────
def build_post(i, p):
    base = '../'
    newer = posts[i - 1] if i > 0 else None
    older = posts[i + 1] if i + 1 < len(posts) else None
    related = [q for q in posts if q is not p and q['category'] == p['category']]
    related += [q for q in posts if q is not p and q not in related]
    related = related[:3]
    ld = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['excerpt'],
          'datePublished': p['date'].isoformat(), 'author': {'@type': 'Organization', 'name': 'Nishtronics Soundlabs'},
          'publisher': {'@type': 'Organization', 'name': 'Nishtronics Soundlabs'},
          'image': (SITE + '/' + p['cover']) if SITE else p['cover']}
    if SITE: ld['mainEntityOfPage'] = f'{SITE}/blog/{p["slug"]}.html'
    extra = social(p['title'] + ' | Nishtronics Soundlabs', p['excerpt'], f'blog/{p["slug"]}.html', p['cover'])
    extra += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'
    bg = HERO_BG.get(p['category'], 'waves')
    nav_pn = ''
    if newer: nav_pn += f'<a class="post-pn newer" href="{newer["slug"]}.html"><span>{svg("chevron-left")}Newer</span><b>{esc(newer["title"])}</b></a>'
    else: nav_pn += '<span></span>'
    if older: nav_pn += f'<a class="post-pn older" href="{older["slug"]}.html"><span>Older{svg("chevron-right")}</span><b>{esc(older["title"])}</b></a>'
    wa_text = ('Hi, I read your article: ' + p['title']).replace(' ', '%20')
    page = head(p['title'] + ' | Nishtronics Soundlabs', p['excerpt'], base, extra) + nav_for(base)
    page += f'''
<section class="page-hero post-hero">
  <img class="page-hero-bg" src="../images/bg/{bg}.webp" alt=""/>
  <div class="page-hero-overlay"></div>
  <div class="page-hero-inner container">
    <span class="page-kicker">{esc(p["category"])}</span>
    <h1>{esc(p["title"])}</h1>
    <div class="post-meta post-meta-hero"><span>{fmt_date(p["date"])}</span><span>{p["mins"]} min read</span><span>Nishtronics team</span></div>
  </div>
</section>

<section class="cut-top" style="background:var(--ink);padding:5rem 0 6rem;">
  <div class="container">
    <article class="post">
      <a class="post-back" href="../blog.html">{svg("chevron-left")}All articles</a>
      <figure class="post-figure"><img src="../{p["cover"]}" alt="" width="1200" height="630"/></figure>
      <div class="prose">
{md(p["body"], True)}
      </div>
      <div class="post-share">
        <span>Share this article</span>
        <a class="btn btn-ghost btn-sm" id="shareWa" href="https://wa.me/" target="_blank" rel="noopener">{svg("whatsapp")}WhatsApp</a>
        <button class="btn btn-ghost btn-sm" id="copyLink" type="button">{svg("link")}<span>Copy link</span></button>
      </div>
      <div class="post-cta">
        <div>
          <h3>Want this done properly?</h3>
          <p>Tell us what you drive and what you want to improve. We will suggest a sensible plan and a clear price before any work starts.</p>
        </div>
        <div class="post-cta-btns">
          <a href="https://wa.me/{WA}?text={esc(wa_text)}" class="btn btn-wa btn-lg" target="_blank" rel="noopener">{svg("whatsapp")}WhatsApp us</a>
          <a href="../booking.html" class="btn btn-gold btn-lg">{svg("calendar")}Book a job</a>
        </div>
      </div>
    </article>

    <div class="post-related">
      <h2>Keep reading</h2>
      <div class="blog-grid">
        {''.join(card(q, '').replace('href="blog/', 'href="').replace('src="images/', 'src="../images/') for q in related)}
      </div>
    </div>
    <div class="post-pns">{nav_pn}</div>
  </div>
</section>

<script>
(function () {{
  var url = location.href.split('#')[0], title = document.title;
  var wa = document.getElementById('shareWa');
  if (wa) wa.href = 'https://wa.me/?text=' + encodeURIComponent(title + ' ' + url);
  var btn = document.getElementById('copyLink');
  if (btn) btn.addEventListener('click', function () {{
    var label = btn.querySelector('span');
    function done() {{ label.textContent = 'Link copied'; setTimeout(function () {{ label.textContent = 'Copy link'; }}, 2000); }}
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, done); else done();
  }});
}})();
</script>
''' + tail(base)
    os.makedirs('blog', exist_ok=True)
    open(f'blog/{p["slug"]}.html', 'w', encoding='utf-8').write(page)

# ───────────────────────── home page block ─────────────────────────
def update_home():
    s = read('index.html')
    a, b = '<!-- BLOG-LATEST:START', '<!-- BLOG-LATEST:END -->'
    if a not in s or b not in s:
        print('note: index.html has no BLOG-LATEST markers, home page block skipped'); return
    block = f'''<!-- BLOG-LATEST:START (generated by tools/build-blog.py, do not edit by hand) -->
<section class="cut-top" style="background:var(--ink-1);padding:9rem 0 8rem;">
  <div class="container">
    <div class="section-head reveal">
      <span class="s-kicker">The Blog</span>
      <h2>Sound <span class="gold">Advice</span></h2>
      <p style="color:var(--t2);max-width:520px;margin:1rem auto 0;line-height:1.7;">Plain-English guides on car audio, home theatre and tracking, from the people who install it.</p>
    </div>
    <div class="blog-grid">
      {''.join(card(p, '') for p in posts[:3])}
    </div>
    <div class="tc" style="margin-top:3rem;"><a href="blog.html" class="btn btn-ghost btn-lg">All articles {svg("arrow-right")}</a></div>
  </div>
</section>
'''
    i, j = s.index(a), s.index(b)
    open('index.html', 'w', encoding='utf-8').write(s[:i] + block + s[j:])

# ───────────────────────── sitemap + feed (need --site) ─────────────────────────
def write_site_files():
    if not SITE: return
    pages = ['index', 'products', 'services', 'gallery', 'blog', 'about', 'contact', 'booking']
    urls = [f'{SITE}/{p}.html' for p in pages] + [f'{SITE}/blog/{p["slug"]}.html' for p in posts]
    open('sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    open('robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {SITE}/sitemap.xml\n')
    items = ''.join(f'  <item><title>{esc(p["title"])}</title><link>{SITE}/blog/{p["slug"]}.html</link><guid>{SITE}/blog/{p["slug"]}.html</guid>'
                    f'<pubDate>{p["date"].strftime("%a, %d %b %Y")} 08:00:00 +0300</pubDate><description>{esc(p["excerpt"])}</description></item>\n' for p in posts)
    open('feed.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f'  <title>Nishtronics Soundlabs: Sound Advice</title><link>{SITE}/blog.html</link>\n  <description>Guides on car audio, home theatre and tracking.</description>\n{items}</channel></rss>\n')

build_index()
for i, p in enumerate(posts): build_post(i, p)
update_home()
write_site_files()
print(f'built blog.html + {len(posts)} posts' + (' + sitemap.xml, robots.txt, feed.xml' if SITE else ''))
