"""Check public files, links, contracts and original visual structure."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
import argparse,ast,hashlib,html,json,re,subprocess
from build_content import ASSETS

ROOT=Path(__file__).resolve().parents[1]
BASELINE='ff6a62aecd1aed08599c04d871f114ddc54cc540'
APPROVED_TERMS_CANONICAL_SHA256='ffbe6576c5768e38f8ad89b95d0223df3647d862f00d7c1297d51bc11844c16a'
def baseline(name):return subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
class Page(HTMLParser):
    def __init__(self,text,reader_layout=False,legal_layout=False):
        super().__init__();self.ids=set();self.links=[];self.shape=[];self.duplicate_ids=[]
        self.reader_layout=reader_layout;self.legal_layout=legal_layout;self.skip_depth=0;self.glossary_link=False;self.app_code=False;self.feed(text)
    def handle_starttag(self,tag,attrs):
        if self.skip_depth:self.skip_depth+=1;return
        if self.legal_layout and ((tag in ('a','span') and dict(attrs).get('class') in ('legal','copyright')) or (tag=='sup' and dict(attrs).get('class')=='cp-brand__trademark')):self.skip_depth=1;return
        if self.reader_layout:
            if tag=='div' and dict(attrs).get('id')=='overview-text':self.skip_depth=1;return
            if tag=='a' and dict(attrs).get('href') in ['glossary.html#section-2','glossary.html#section-3','glossary.html#section-4']:
                self.glossary_link=True;return
            if tag=='code':self.app_code=True;return
            attrs=[(k,'ctx' if k=='class' and v=='ctx dw' else v) for k,v in attrs]
        self.shape.append(('start',tag,attrs));a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicate_ids.append(a['id'])
            self.ids.add(a['id'])
        for attr in ('href','src','data-index'):
            if a.get(attr):self.links.append(a[attr])
    def handle_endtag(self,tag):
        if self.skip_depth:self.skip_depth-=1;return
        if self.reader_layout:
            if tag=='a' and self.glossary_link:self.glossary_link=False;return
            if tag=='code' and self.app_code:self.app_code=False;return
        self.shape.append(('end',tag))

def reader_checks(files,pages):
    config=json.loads((ROOT/'content-source/site.json').read_bytes());failures=[]
    title_count=0;footer_links=0
    clean=lambda s:html.unescape(re.sub(r'<[^>]+>','',s)).strip()
    for p in config['pages']:
        name=config['version_path']+'/'+p['slug']+'.html';text=(ROOT/name).read_text(encoding='utf-8')
        h1=re.search(r'<h1[^>]*>(.*?)</h1>',text,re.S);crumb=re.search(r'<div class="breadcrumb">(.*?)</div>',text,re.S)
        current=re.search(r'<a[^>]*aria-current="page"[^>]*>(.*?)</a>',text,re.S)
        if not h1 or clean(h1[1])!=p['title'] or not current or clean(current[1])!=p['title'] or not crumb or not clean(crumb[1]).endswith(p['title']):failures.append('reader title mismatch '+name)
        else:title_count+=1
        for block in re.findall(r'<(?:nav class="page-next"|footer class="page-foot")[^>]*>.*?</(?:nav|footer)>',text,re.S):
            hrefs=re.findall(r'href="([^"]+)"',block);footer_links+=len(hrefs)
            if len(hrefs)!=len(set(hrefs)):failures.append('repeated next/footer link '+name)
            if any(urlsplit(urljoin('https://docs.invalid/'+name,h)).path=='/'+name for h in hrefs):failures.append('self next/footer link '+name)
    overview=(ROOT/'v0.7/index.html').read_text(encoding='utf-8')
    normalized=Page(overview,reader_layout=True,legal_layout=True).shape==Page(baseline('v0.7/index.html').decode('utf-8')).shape
    if not normalized:failures.append('overview layout changed beyond text alternative and glossary links')
    if '<svg class="ctx dw"' not in overview or 'id="overview-text"' not in overview or overview.count('<code>app</code>')!=1 or any(q in overview for q in '①②③④⑤'):failures.append('overview mobile alternative or numbering')
    for f in (ROOT/'content-source/pages').glob('*.md'):
        if f.stem in ['glossary','changelog']:continue
        text=re.sub(r'```.*?```','',f.read_text(encoding='utf-8'),flags=re.S)
        if any(term in text for term in ['お客様専用アプリ','あなたのアプリ','インフラ','CoreAPI','2要求','要求のたび','要求ごと']):failures.append('reader vocabulary drift '+f.name)
    fixed='5a4649e6521e75e2069d6a68e629c5d557db1d12'
    protected=['v0.7/openapi.json','v0.7/api-inventory.json','v0.7/mcp-tools.json']+[n for n in files if n.startswith('v0.7/examples/')]
    for n in protected:
        if (ROOT/n).read_bytes()!=subprocess.check_output(['git','show',fixed+':'+n],cwd=ROOT):failures.append('reader revision changed contract/example '+n)
    for n in ['v0.7/api.html']:
        old=subprocess.check_output(['git','show',fixed+':'+n],cwd=ROOT).decode('utf-8');new=(ROOT/n).read_text(encoding='utf-8')
        if re.search(r'<h1.*?(?=<footer)',old,re.S)[0]!=re.search(r'<h1.*?(?=<footer)',new,re.S)[0]:failures.append('reader revision changed API reference body')
    principles=(ROOT/'v0.7/principles.html').read_text(encoding='utf-8');next_block=re.search(r'<nav class="page-next".*?</nav>',principles,re.S)[0]
    if re.findall(r'href="([^"]+)"',next_block)[:2]!=['quickstart.html','versions.html']:failures.append('principles next steps')
    mcp_guide=(ROOT/'content-source/pages/mcp.md').read_text(encoding='utf-8')
    if '## macOS向けMCPの接続方法' not in mcp_guide or 'macOSでの導入準備' in mcp_guide or 'python3 --version' in mcp_guide or '| macOS | {{準備中}}' not in mcp_guide or '現行配布版1.0.1では、Keychainを使うキーの保存・読取が未対応' not in mcp_guide or '接続方式と提供時期は未確定' not in mcp_guide:failures.append('MCP macOS guidance scope')
    if '管理サイトのブラウザー利用や、顧客アプリ・基盤APIの開発でmacOSを使うこととは別' not in mcp_guide:failures.append('MCP OS scope broadened to service')
    for name in ['principles','versions']:
        if '| macOS向けMCPの接続方法 | {{準備中}} |' not in (ROOT/f'content-source/pages/{name}.md').read_text(encoding='utf-8'):failures.append('macOS direction status mismatch '+name)
    return failures,{'page_titles_aligned':title_count,'next_and_footer_links_checked':footer_links,'no_self_or_duplicate_next_and_footer_links':not any('footer link' in f for f in failures),'overview_layout_preserved_except_approved_additions':normalized,'machine_contract_and_example_files_byte_identical_to_revision12':protected,'api_reference_body_byte_identical_to_revision12':True}

def protocol(node):
    if isinstance(node,dict):return {k:protocol(v) for k,v in node.items() if k not in ['summary','description','title','example','examples','client_ids'] and not k.startswith('x-')}
    if isinstance(node,list):return [protocol(v) for v in node]
    return node

def legal_checks(files):
    failures=[];config=json.loads((ROOT/'content-source/site.json').read_bytes())
    canonical=lambda s:'\n'.join(re.sub(r'^#{1,6}\s+','',line).strip() for line in s.splitlines() if line.strip())+'\n'
    source=canonical((ROOT/'content-source/pages/terms.md').read_text(encoding='utf-8'))
    source_sha=hashlib.sha256(source.encode('utf-8')).hexdigest()
    if source_sha!=APPROVED_TERMS_CANONICAL_SHA256:failures.append('approved legal source text changed')
    if canonical((ROOT/'v0.7/guide/terms.md').read_text(encoding='utf-8'))!=source:failures.append('legal Markdown differs from approved source')
    doc=(ROOT/'v0.7/terms.html').read_text(encoding='utf-8');body=re.search(r'<h1.*?(?=<footer)',doc,re.S)[0]
    body=re.sub(r'<nav class="page-toc".*?</nav>','',body,flags=re.S)
    rendered='\n'.join(html.unescape(re.sub(r'<[^>]+>','',text)).strip() for _,text in re.findall(r'<(h1|h2|p)[^>]*>(.*?)</\1>',body,re.S))+'\n'
    if rendered!=source:failures.append('rendered legal text differs from approved source')
    if '®' in rendered or '専門家' in rendered or 'Meta X Design' in rendered:failures.append('unapproved trademark/copyright/legal note')
    checked=0
    for n in ['index.html']+['v0.7/'+p['slug']+'.html' for p in config['pages']]:
        text=(ROOT/n).read_text(encoding='utf-8');footer=re.search(r'<footer class="page-foot".*?</footer>',text,re.S)[0]
        if footer.count(config['copyright'])!=1:failures.append('copyright footer '+n)
        if n=='v0.7/terms.html':
            if '<span class="legal">利用条件・免責事項</span>' not in footer:failures.append('legal self footer '+n)
        else:
            href='v0.7/terms.html' if n=='index.html' else 'terms.html'
            if f'<a class="legal" href="{href}">' not in footer:failures.append('legal footer route '+n)
        if not re.search(r'<a href="(?:v0.7/)?terms.html" class="legal"',text):failures.append('legal sidebar route '+n)
        if text.count('class="cp-brand__trademark"')!=1:failures.append('brand trademark marker '+n)
        main_text=re.search(r'<main.*?</main>',text,re.S)[0]
        if main_text.count('™')!=(1 if n in ['index.html','v0.7/index.html','v0.7/terms.html'] else 0):failures.append('trademark symbol outside approved places '+n)
        checked+=1
    fixed='eb7accac48182a03dde99f9b475c5ef118079d7d'
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',fixed],cwd=ROOT,text=True).splitlines()
    licenses=[n for n in names if re.search(r'(?i)(?:^|/)(?:license|copying|notice)(?:\.|$)',n)]
    protected=licenses+['content-source/pages/mcp.md']+[n for n in files if n.startswith('v0.7/examples/')]
    for n in protected:
        if (ROOT/n).read_bytes()!=subprocess.check_output(['git','show',fixed+':'+n],cwd=ROOT):failures.append('legal change altered licensed/distributed/sample source '+n)
    if 'v0.7/terms.html' not in (ROOT/'sitemap.xml').read_text(encoding='utf-8'):failures.append('legal sitemap route')
    return failures,{'approved_canonical_text_sha256':source_sha,'source_markdown_and_rendered_text_match_approved_text':not any('text' in f or 'source' in f for f in failures),'primary_pages_with_legal_navigation_and_copyright':checked,'existing_license_files_preserved':licenses,'mcp_guide_and_sample_files_preserved':protected,'registered_trademark_symbol_absent':True,'trademark_symbol_limited_to_approved_places':not any('trademark' in f for f in failures)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raw-openapi');ap.add_argument('--mcp-source');ap.add_argument('--credential-source');ap.add_argument('--report');args=ap.parse_args()
    failures=[];manifest=json.loads((ROOT/'manifest.json').read_bytes());files=manifest['files'];pages={};links=0;md_links=0
    for name,expected in files.items():
        raw=(ROOT/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:failures.append('hash '+name)
        text=html.unescape(raw.decode('utf-8'))
        for phrase in ['案件','morita@','伴走支援','大手企業のセキュリティ水準','design-images','design-blue.png','デザイン見本','お客様ごとの専用環境']:
            if phrase in text:failures.append('non-generic wording '+name+' '+phrase)
        for address in re.findall(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+\.[A-Za-z]{2,}',text):
            domain=address.rsplit('@',1)[1].lower()
            if not domain.endswith('.invalid') and domain not in ['example.com','example.net','example.org']:failures.append('non-synthetic email '+name)
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
            elif p.fragment and target.suffix=='.html':
                key=target.resolve().relative_to(ROOT).as_posix()
                if key not in pages or unquote(p.fragment) not in pages[key].ids:failures.append('Markdown HTML anchor '+name+' '+link)
    assets={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ASSETS}
    for n,expected in ASSETS.items():
        if assets[n]!=expected or (ROOT/n).read_bytes()!=baseline(n):failures.append('asset changed '+n)
    unchanged_structure={n:Page(baseline(n).decode('utf-8')).shape==pages[n].shape for n in ['index.html','v0.7/index.html']}
    home_normalized=Page((ROOT/'index.html').read_text(encoding='utf-8'),legal_layout=True).shape==Page(baseline('index.html').decode('utf-8')).shape
    if not home_normalized:failures.append('home visual DOM changed beyond legal links and copyright')
    reader_failures,reader_report=reader_checks(files,pages);failures.extend(reader_failures)
    legal_failures,legal_report=legal_checks(files);failures.extend(legal_failures)
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
    assert spec['x-error-code-usage']['FOLDER_LIMIT_REACHED']=='other_core_contract_not_mapped_to_public_operation'
    assert not any('FOLDER_LIMIT_REACHED' in json.dumps(op) for methods in spec['paths'].values() for op in methods.values())
    credential_checked=None;mcp_os_checked=None
    if args.credential_source:
        source_bytes=Path(args.credential_source).read_bytes();provenance=json.loads((ROOT/'v0.7/provenance.json').read_bytes())
        assert hashlib.sha256(source_bytes).hexdigest()==provenance['mcp']['credential_store_source_sha256']
        fn=next(n for n in ast.parse(source_bytes).body if isinstance(n,ast.FunctionDef) and n.name=='credential')
        assert isinstance(fn.body[0],ast.If)
        expr=compile(ast.Expression(fn.body[0].test),'<credential-validation-only>','eval')
        for name,rejected in [('customer-imports',False),('0_a-z',False),('Customer-imports',True),('path/name',True),('has space',True),('',True),('a'*47+'-'+'0'*16,False),('a'*48+'-'+'0'*16,True)]:
            assert bool(eval(expr,{'__builtins__':{},'len':len,'any':any,'name':name}))==rejected,name
        # Inspect the fixed source, without invoking any OS credential store.
        assert "os.name == 'nt'" in source_bytes.decode('utf-8') and 'CryptProtectData' in source_bytes.decode('utf-8')
        assert 'secret-tool' in source_bytes.decode('utf-8') and 'Keychain' not in source_bytes.decode('utf-8')
        if args.mcp_source:
            cli=ast.parse(Path(args.mcp_source).read_bytes())
            options={a.value for n in ast.walk(cli) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' for a in n.args if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.startswith('--')}
            assert options=={'--base','--directory','--credential-name','--save-key'}
            mcp_os_checked=True
        credential_checked=True
    report={'passed':not failures,'documentation_revision':manifest['documentation_revision'],'public_files':len(files),'html_pages':len(pages),'checked_html_links':links,'checked_markdown_links':md_links,'failures':failures,'original_asset_sha256':assets,'home_and_overview_DOM_structure_unchanged':unchanged_structure,'original_navigation_page_count':22,'existing_operations_preserved':len(old_ops),'api_operations':len(new_ops),'added_operations':sorted(x[2] for x in new_ops-old_ops),'raw_protocol_structure_identical':raw_matches,'raw_authority_identical_except_private_client_allowlist':authority_matches,'mcp_tools':len(mcp['tools']),'mcp_input_schema_and_annotations_match_pinned_source':mcp_matches,'synthetic_examples':len(samples),'example_operation_coverage':len({(q['method'],q['path']) for q in samples})}
    report.update(generic_wording_and_email_guard_passed=not failures,folder_limit_not_mapped_to_public_operation=True,credential_name_validation_checked_without_store_access=credential_checked,json_examples=sum('body_base64' not in q for q in samples),binary_examples=sum('body_base64' in q for q in samples))
    report['reader_review_checks']=reader_report
    report['mcp_os_support_and_cli_inspected_without_store_or_client_execution']=mcp_os_checked
    report['home_layout_preserved_except_legal_links_copyright_and_trademark']=home_normalized
    report['approved_documentation_terms_checks']=legal_report
    if args.report:Path(args.report).write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
if __name__=='__main__':main()
