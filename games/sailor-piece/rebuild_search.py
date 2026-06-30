#!/usr/bin/env python3
"""
Sailor Piece Wiki – Search Index Rebuilder
"""
import json, re, pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).parent
PAGES = {
  'index.html':   {'title':'Sailor Piece Wiki Hub', 'cat':'Hub', 'icon':'⚓'},
  'races.html':   {'title':'Races', 'cat':'Traits', 'icon':'🧬'},
  'clans.html':   {'title':'Clans', 'cat':'Traits', 'icon':'🔥'},
  'bloodlines.html':{'title':'Bloodlines','cat':'Traits','icon':'🩸'},
  'fruits.html':  {'title':'Devil Fruits','cat':'Combat','icon':'🍇'},
  'swords.html':  {'title':'Swords','cat':'Combat','icon':'⚔️'},
  'melee.html':   {'title':'Fighting Styles','cat':'Combat','icon':'👊'},
  'codes.html':   {'title':'Codes','cat':'Guides','icon':'🎁'},
  'items.html':   {'title':'Items','cat':'Combat','icon':'🎒'}
}

def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s
def slugify(s):
    s = s.lower(); s = re.sub(r'[^a-z0-9]+', '-', s); return s.strip('-')

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

entries = []
for fname, meta in PAGES.items():
    fpath = ROOT / fname
    if not fpath.exists(): continue
    html = fpath.read_text(encoding='utf-8')
    found = 0
    if HAS_BS4:
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.select('table.db-table tr'):
            if tr.find('th'): continue
            name_el = tr.select_one('.fruit-name, .bloodline-name, .race-name, .clan-name, .sword-name, .melee-name, .style-name, .code-string, .item-name')
            if not name_el: continue
            name = name_el.get_text(strip=True)
            full_text = tr.get_text(' ', strip=True)
            entries.append({'t': name, 'u': f"{fname}#{slugify(name)}", 'c': meta['title'], 'i': meta['icon'], 's': full_text[:240]})
            found += 1
        for card in soup.select('.code-card'):
            code_el = card.select_one('.code-string')
            if not code_el: continue
            name = code_el.get_text(strip=True)
            full_text = card.get_text(' ', strip=True)
            entries.append({'t': name, 'u': f"{fname}#{slugify(name)}", 'c': meta['title'], 'i': meta['icon'], 's': full_text[:240]})
            found += 1
    else:
        for tr_html in re.finditer(r'<tr>(.*?)</tr>', html, re.S|re.I):
            tr = tr_html.group(1)
            if '<th' in tr.lower(): continue
            m = re.search(r'class="(?:fruit-name|bloodline-name|race-name|clan-name|sword-name|melee-name|style-name|item-name)">([^<]+)<', tr)
            if not m: continue
            name = strip_tags(m.group(1))
            full_text = strip_tags(tr)
            entries.append({'t': name, 'u': f"{fname}#{slugify(name)}", 'c': meta['title'], 'i': meta['icon'], 's': full_text[:240]})
            found += 1
    body_text = strip_tags(re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S))
    entries.append({'t': meta['title'], 'u': fname, 'c': meta['cat'], 'i': meta['icon'], 's': body_text[:220]})
    print(f"{fname:20} → {found} items")

# de-dupe
seen=set(); dedup=[]
for e in entries:
    k=(e['t'].lower(), e['u'])
    if k in seen: continue
    seen.add(k); dedup.append(e)

print(f"\nTotal: {len(dedup)} search entries")
out_json = ROOT / 'assets' / 'search-index.json'
out_json.write_text(json.dumps(dedup, ensure_ascii=False), encoding='utf-8')
print(f"Wrote {out_json}")

# inline into wiki.js
wiki_js = ROOT / 'assets' / 'wiki.js'
if wiki_js.exists():
    js_text = wiki_js.read_text(encoding='utf-8')
    new_index = f"const SEARCH_INDEX = {json.dumps(dedup, ensure_ascii=False)};"
    import re as _re
    new_js, n = _re.subn(r'const SEARCH_INDEX\s*=\s*\[.*?];', new_index, js_text, count=1, flags=_re.S)
    if n==0:
        new_js, n = _re.subn(r'(?:let|var)\s+SEARCH_INDEX\s*=\s*\[.*?];', new_index, js_text, count=1, flags=_re.S)
    if n>0:
        wiki_js.write_text(new_js, encoding='utf-8')
        print(f"Updated {wiki_js}")
    else:
        print("WARNING: could not find SEARCH_INDEX in wiki.js")
print("Done! Ctrl+F5 in browser.")
