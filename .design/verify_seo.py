from html.parser import HTMLParser
from pathlib import Path
import json, xml.etree.ElementTree as ET, urllib.request
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.tags.append((tag,dict(attrs)))
root=Path('.')
p=Page(root.joinpath('index.html').read_text(encoding='utf-8-sig'))
meta={a.get('name',a.get('property')):a.get('content') for t,a in p.tags if t=='meta'}
assert sum(t=='h1' for t,a in p.tags)==1
assert next(a for t,a in p.tags if t=='html')['lang']=='uk'
assert len([a for t,a in p.tags if t=='link' and a.get('rel')=='canonical'])==1
for key in ['description','og:title','og:description','og:url','og:image','og:image:width','og:image:height','og:image:alt','twitter:card','twitter:image','twitter:image:alt']:
    assert meta.get(key), key
for t,a in p.tags:
    for key in ['src','href']:
        v=a.get(key,'')
        if v.startswith('/') and not v.startswith('//') and v!='/': assert root.joinpath(v[1:]).is_file(),v
text=root.joinpath('index.html').read_text(encoding='utf-8-sig')
structured=json.loads(text.split('<script type="application/ld+json">')[1].split('</script>')[0])
assert len(structured['@graph'])==2
assert all(x['@type'] in ['WebPage','WebSite'] for x in structured['@graph'])
ET.parse('sitemap.xml'); assert 'https://clothes.webart.work/sitemap.xml' in root.joinpath('robots.txt').read_text()
assert 'noindex' in root.joinpath('404.html').read_text(encoding='utf-8-sig')
for url in ['/', '/styles.css','/favicon.svg','/assets/clothes-editorial.jpg','/assets/clothes-social.jpg','/robots.txt','/sitemap.xml','/404.html']:
    with urllib.request.urlopen('http://127.0.0.1:4173'+url) as r: assert r.status==200
print('PASS: metadata, schema JSON, sitemap XML, robots, local assets, H1, language, 404 noindex and all 8 HTTP resources.')
