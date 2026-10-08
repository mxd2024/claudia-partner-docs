"""Check public files, links, contracts and original visual structure."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
import argparse,ast,hashlib,json,re,subprocess
from build_content import ASSETS

ROOT=Path(__file__).resolve().parents[1]
BASELINE='ff6a62aecd1aed08599c04d871f114ddc54cc540'
def baseline(name):return subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.links=[];self.shape=[];self.duplicate_ids=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.shape.append(('start',tag,attrs));a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicate_ids.append(a['id'])
            self.ids.add(a['id'])
        for attr in ('href','src','data-index'):
            if a.get(attr):self.links.append(a[attr])
    def handle_endtag(self,tag):self.shape.append(('end',tag))

def protocol(node):
    if isinstance(node,dict):return {k:protocol(v) for k,v in node.items() if k not in ['summary','description','title','example','examples','client_ids'] and not k.startswith('x-')}
    if isinstance(node,list):return [protocol(v) for v in node]
    return node
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raw-openapi');ap.add_argument('--mcp-source');ap.add_argument('--report');args=ap.parse_args()
    failures=[];manifest=json.loads((ROOT/'manifest.json').read_bytes());files=manifest['files'];pages={};links=0;md_links=0
    for name,expected in files.items():
        raw=(ROOT/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:failures.append('hash '+name)
        if name.endswith('.html'):
            pages[name]=Page(raw.decode('utf-8'))
            if pages[name].duplicate_ids:failures.append('duplicate ids '+name)
    base=manifest['public_base_url']
    for name,page in pages.items():
        for link in page.links:
            url=urljoin(base+name,link)
            if not url.startswith(base):continue
            p=urlsplit(url);target=unquote(p.path[len(urlsplit(base).path):]) or 'index.html'
            if target.endswith('/'):target+='index.html'
            links+=1
            if target not in files and target!='manifest.json':failures.append('link '+name+' '+link)
            elif p.fragment and target in pages and unquote(p.fragment) not in pages[target].ids:failures.append('anchor '+name+' '+link)
    for name in files:
        if not name.endswith('.md'):continue
        text=(ROOT/name).read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',text):
            p=urlsplit(link)
            if p.scheme or link.startswith('#'):continue
            md_links+=1;target=(ROOT/name).parent/unquote(p.path)
            if not target.resolve().is_relative_to(ROOT) or not target.is_file():failures.append('Markdown link '+name+' '+link)
    assets={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ASSETS}
    for n,expected in ASSETS.items():
        if assets[n]!=expected or (ROOT/n).read_bytes()!=baseline(n):failures.append('asset changed '+n)
    unchanged_structure={n:Page(baseline(n).decode('utf-8')).shape==pages[n].shape for n in ['index.html','v0.7/index.html']}
    if not all(unchanged_structure.values()):failures.append('home or overview visual DOM changed')
    spec=json.loads((ROOT/'v0.7/openapi.json').read_bytes());inv=json.loads((ROOT/'v0.7/api-inventory.json').read_bytes())
    old=json.loads(baseline('v0.7/openapi.json'))
    old_ops={(method,path,op['operationId']) for path,methods in old['paths'].items() for method,op in methods.items()}
    new_ops={(method,path,op['operationId']) for path,methods in spec['paths'].items() for method,op in methods.items()}
    assert old_ops<=new_ops and {op[2] for op in new_ops-old_ops}=={'service.metadata','service.import'}
    assert {(r['method'].lower(),r['path'],r['operation_id']) for r in inv['routes']}==new_ops
    assert len(new_ops)==inv['route_count']==134
    for path,method in [('/v2/service/tables/{collection}','get'),('/v2/service/tables/{collection}/import','post')]:
        assert spec['paths'][path][method]['x-required-authority']['actor_types']==['service']
    raw_matches=None;authority_matches=None
    if args.raw_openapi:
        raw_bytes=Path(args.raw_openapi).read_bytes();assert hashlib.sha256(raw_bytes).hexdigest()==manifest['source_openapi_sha256']
        raw=json.loads(raw_bytes);raw_matches=protocol(raw)==protocol(spec);assert raw_matches
        authority_matches=True
        for path,methods in raw['paths'].items():
            for method,op in methods.items():
                source=json.loads(json.dumps(op.get('x-required-authority',{})));source.pop('client_ids',None)
                assert source==spec['paths'][path][method].get('x-required-authority',{}),(path,method,'authority changed')
    mcp=json.loads((ROOT/'v0.7/mcp-tools.json').read_bytes());assert len(mcp['tools'])==8 and mcp['adapter_version']=='1.0.1'
    mcp_matches=None
    if args.mcp_source:
        source_bytes=Path(args.mcp_source).read_bytes();provenance=json.loads((ROOT/'v0.7/provenance.json').read_bytes())
        assert hashlib.sha256(source_bytes).hexdigest()==provenance['mcp']['client_source_sha256']
        tree=ast.parse(source_bytes);defs=None
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOOLS' for t in node.targets):defs=ast.literal_eval(node.value)
        assert defs is not None
        actual={t['name']:t for t in mcp['tools']};assert set(actual)=={t[0] for t in defs}
        for name,desc,props,required,readonly in defs:
            assert actual[name]['inputSchema']=={'type':'object','properties':props,'required':required,'additionalProperties':False}
            assert actual[name]['annotations']=={'readOnlyHint':readonly,'destructiveHint':name=='imports_run','idempotentHint':name in ('imports_run','imports_status','imports_verify'),'openWorldHint':False}
        mcp_matches=True
    samples=json.loads((ROOT/'v0.7/examples/public-requests.json').read_bytes())
    for q in samples:assert str(q['status']) in spec['paths'][q['path']][q['method'].lower()]['responses']
    report={'passed':not failures,'documentation_revision':manifest['documentation_revision'],'public_files':len(files),'html_pages':len(pages),'checked_html_links':links,'checked_markdown_links':md_links,'failures':failures,'original_asset_sha256':assets,'home_and_overview_DOM_structure_unchanged':unchanged_structure,'original_navigation_page_count':22,'existing_operations_preserved':len(old_ops),'api_operations':len(new_ops),'added_operations':sorted(x[2] for x in new_ops-old_ops),'raw_protocol_structure_identical':raw_matches,'raw_authority_identical_except_private_client_allowlist':authority_matches,'mcp_tools':len(mcp['tools']),'mcp_input_schema_and_annotations_match_pinned_source':mcp_matches,'synthetic_examples':len(samples),'example_operation_coverage':len({(q['method'],q['path']) for q in samples})}
    if args.report:Path(args.report).write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
if __name__=='__main__':main()
