"""Verify published paths, anchors, checksums, coverage and public-only boundaries."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT/'site-source/site.json').read_bytes())
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
BASE = manifest['public_base_url']
files = manifest['files']
failures = []


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.links=[]; self.ids=set(); self.duplicates=[]; self.h1=0
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids: self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        for attr in ('href','src','data-index','data-destination'):
            if a.get(attr): self.links.append(a[attr])


pages={}
checked=0
for name,expected in files.items():
    path=ROOT/name
    if not path.is_file() or path.is_symlink(): failures.append('missing/symlink '+name); continue
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected: failures.append('hash '+name)
    text=raw.decode('utf-8')
    for address in re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text):
        if not address.lower().endswith('.invalid'): failures.append('unverified email '+name)
    if re.search(r'案件|design-images|design-blue\.png|デザイン(?:原本|見本|画像)|大手企業のセキュリティ|修正版の提供日は未定',text):
        failures.append('public wording regression '+name)
    if re.search(r'github\.com/mxd2024/claudia-partner-(?:infrastructure|customer|provider|family)|/home/eluga/|[DE]:[\\/]|(?:gh[pousr]_[A-Za-z0-9]{20,})|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+\.',text):
        failures.append('private content '+name)
    if name.endswith('.html'):
        pages[name]=Page(text)
        if pages[name].duplicates: failures.append('duplicate ids '+name+' '+str(pages[name].duplicates))
        if pages[name].h1!=1: failures.append('h1 '+name)
    if name.startswith(('tools/','site-source/','.git/','.qa/')): failures.append('unselected source '+name)


def check_link(origin,link):
    global checked
    if link.startswith(('mailto:','tel:','data:')): return
    absolute=urljoin(BASE+origin,link)
    parsed=urlsplit(absolute)
    old='https://mxd2024.github.io/claudia-partner-docs/'
    if absolute.startswith(old): relative=absolute[len(old):].split('#')[0].split('?')[0]
    elif absolute.startswith(BASE): relative=parsed.path[len(urlsplit(BASE).path):]
    else:
        if parsed.scheme!='https': failures.append('insecure external link '+origin+' '+link)
        return
    relative=unquote(relative) or 'index.html'
    if relative.endswith('/'): relative+='index.html'
    if relative not in files and relative!='manifest.json': failures.append('link '+origin+' -> '+link); return
    checked+=1
    if parsed.fragment and relative in pages and unquote(parsed.fragment) not in pages[relative].ids:
        failures.append('anchor '+origin+' -> '+link)


for name,parsed in pages.items():
    for link in parsed.links: check_link(name,link)
for name in files:
    if name.endswith('.md'):
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',(ROOT/name).read_text(encoding='utf-8')):
            check_link(name,link)
links=json.loads((ROOT/'links.json').read_text(encoding='utf-8'))
for version in links['versions'].values():
    for link in version['links'].values(): check_link('links.json',link)
search=json.loads((ROOT/'v0.7/search-index.json').read_text(encoding='utf-8'))
for entry in search['entries']: check_link('v0.7/search-index.json',entry['u'])
spec=json.loads((ROOT/'v0.7/openapi.json').read_text(encoding='utf-8'))
inventory=json.loads((ROOT/'v0.7/api-inventory.json').read_text(encoding='utf-8'))
operation_count=sum(m in {'get','post','put','patch','delete'} for methods in spec['paths'].values() for m in methods)
assert operation_count==len(inventory['routes'])==inventory['route_count']==inventory['openapi_route_count']==config['expected_operations']
mcp=json.loads((ROOT/'v0.7/mcp-tools.json').read_bytes())
provenance=json.loads((ROOT/'v0.7/provenance.json').read_bytes())
assert len(mcp['tools'])==config['expected_mcp_tools']==provenance['mcp']['tool_count']
assert mcp['adapter_version']==config['mcp_adapter_version']==provenance['mcp']['adapter_version']==manifest['mcp_adapter_version']
assert spec['info']['version']==inventory['api_version']==provenance['api_version']==config['version']==manifest['version']
assert config['source_api_sha256']==inventory['source_openapi_sha256']==provenance['source_openapi_sha256']==manifest['source_openapi_sha256']
assert config['source_api_commit']==inventory['source_commit']==provenance['source_openapi_commit']==manifest['source_openapi_commit']
assert config['public_openapi_sha256']==provenance['public_openapi_sha256']==files['v0.7/openapi.json']
assert config['revision']==manifest['documentation_revision']==provenance['documentation_revision']
assert config['updated']==manifest['updated']==provenance['reviewed_date']
assert config['contract_snapshot_date']==manifest['contract_snapshot_date']==inventory['contract_snapshot_date']==provenance['contract_snapshot_date']
assert len(json.loads((ROOT/'v0.7/examples/public-requests.json').read_text(encoding='utf-8')))==60
for route in inventory['routes']:
    operation=spec['paths'][route['path']][route['method'].lower()]
    assert operation['operationId']==route['operation_id']
    assert operation['x-availability']==route['availability']
    identity='op-'+re.sub(r'[^a-zA-Z0-9_-]','-',route['operation_id'])
    if identity not in pages['v0.7/api.html'].ids: failures.append('legacy operation anchor '+identity)
    if identity not in pages['v0.7/api-'+route['group']+'.html'].ids: failures.append('operation detail '+identity)
for path,method,identity in [('/v2/service/tables/{collection}','get','service.metadata'),('/v2/service/tables/{collection}/import','post','service.import')]:
    operation=spec['paths'][path][method]
    assert operation['operationId']==identity and operation['x-availability']=='環境による'
    assert operation['x-required-authority']['actor_types']==['service']
def check_refs(node):
    if isinstance(node,dict):
        if '$ref' in node:
            ref=node['$ref']; assert ref.startswith('#/'),ref
            target=spec
            for part in ref[2:].split('/'): target=target[part.replace('~1','/').replace('~0','~')]
        for value in node.values(): check_refs(value)
    elif isinstance(node,list):
        for value in node: check_refs(value)
check_refs(spec)
assert (ROOT/'v0.7/api.html').stat().st_size < 120*1024
for name in ('openapi.json','api-inventory.json','mcp-tools.json','examples/public-requests.json'):
    text=(ROOT/'v0.7'/name).read_text(encoding='utf-8')
    urls=re.findall(r'https?://[^\s<>"\\]+',text)
    for url in urls:
        if not (urlsplit(url).hostname or '').endswith('.invalid'): failures.append('real endpoint in contract '+name)
result={'passed':not failures,'public_files':len(files),'html_pages':len(pages),'checked_internal_links':checked,'broken_links_or_anchors':len(failures),'api_operations':operation_count,'mcp_tools':len(mcp['tools']),'mcp_adapter_version':mcp['adapter_version'],'synthetic_examples':60,'api_index_bytes':(ROOT/'v0.7/api.html').stat().st_size,'contract_hash_and_version_consistency':True,'all_openapi_refs_resolved':True,'public_wording_scan':not any('wording' in x or 'email' in x for x in failures),'failures':failures}
print(json.dumps(result,ensure_ascii=False,indent=2))
if failures: sys.exit(1)
