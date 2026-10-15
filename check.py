"""Check generated page links, image assets, headings and metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set(); self.links=[]; self.h1=0; self.meta=set(); self.images=[]

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='meta': self.meta.add(a.get('name',a.get('property','')))
        if tag=='a' and 'href' in a: self.links.append(a['href'])
        if tag in ['img','script','link']:
            value=a.get('src') if tag!='link' else a.get('href')
            if value:self.links.append(value)
        if tag=='img':self.images.append(a)


pages={}
for path in [ROOT/'index.html',*(ROOT/'projects').glob('*.html')]:
    p=Page(); p.feed(path.read_text(encoding='utf-8')); pages[path.resolve()]=p
errors=[]
for path,p in pages.items():
    if p.h1!=1:errors.append(f'{path.name}: expected one H1')
    for name in ['description','viewport','og:title','og:image']:
        if name not in p.meta: errors.append(f'{path.name}: missing {name}')
    for img in p.images:
        if not img.get('alt'):errors.append(f'{path.name}: image missing alt')
    for href in p.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if not target.exists():errors.append(f'{path.name}: missing target {href}')
        if u.fragment and target in pages and u.fragment not in pages[target].ids:
            errors.append(f'{path.name}: missing anchor {href}')
for p in (ROOT/'assets').glob('*.svg'): ET.parse(p)
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, local links/assets/anchors, metadata, H1s, alt text and SVG XML.')
