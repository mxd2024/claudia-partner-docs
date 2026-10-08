"""Regenerate content using the original site renderer; never write visual assets."""
from pathlib import Path
import argparse, hashlib, json, re
from urllib.parse import urlsplit, urljoin
import public_renderer as r

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'content-source'
ASSETS={
 'v0.7/style.css':'b273b1f54aaecbd1fa1853b49d98869faf87adfbd71105b914c46eaed9125187',
 'v0.7/brand.css':'052b53237fc380d2e3d0585eeb72e8f0829ad934eb2222cb0af14c0e5ff9fd69',
 'v0.7/app.js':'4a39df857644a38b97b738bbd2e675dbf87143c20ba7a7ee37826cfbb0c70040',
 'v0.7/favicon.svg':'f820d227695b731ea048b1d41bde23c05cea16623257e3c4ac57fc3a58af42e1',
 'v0.7/claudia-partner-mark.svg':'f820d227695b731ea048b1d41bde23c05cea16623257e3c4ac57fc3a58af42e1',
}

def text_link(link,config):
    # Markdown is usable directly in this public repository, without private paths.
    m=re.fullmatch(r'([a-z0-9-]+)\.html(#.*)?',link)
    if m and m[1]=='api':return '../openapi.json'
    if m and any(p['slug']==m[1] for p in config['pages']):return m[1]+'.md'
    if urlsplit(link).scheme or link.startswith('#'):return link
    return '../'+link

def outputs():
    c=r.read_json(SOURCE/'site.json');vp=c['version_path']
    # Existing machine-readable public files are the content inputs as well.
    # This avoids duplicating the entire OpenAPI in a second source directory.
    spec=r.read_json(ROOT/vp/'openapi.json')
    inv=r.read_json(ROOT/vp/'api-inventory.json')
    mcp=r.read_json(ROOT/vp/'mcp-tools.json')
    samples=r.read_json(ROOT/vp/'examples/public-requests.json')
    assert spec['info']['version']==inv['api_version']==c['version']
    assert len(inv['routes'])==inv['route_count']==inv['openapi_route_count']==134
    assert mcp['adapter_version']=='1.0.1' and len(mcp['tools'])==8
    gen={'coverage':r.coverage(inv,mcp),
      'error-codes':r.table(['HTTP','code','意味と対応'],[[row[0],'<code>'+r.e(row[1])+'</code>',r.inline(row[2])] for row in r.error_rows(spec)]),
      'mcp-tools':'\n'.join(f'<details class="tool" id="tool-{r.e(t["name"])}"><summary>{r.e(t["name"])}</summary><div class="opbody"><p>{r.e(t["description"])}</p>{r.code(t)}</div></details>' for t in mcp['tools']),
      'figure-connection':(SOURCE/'figures/connection.html').read_text(encoding='utf-8').strip()}
    retries=[]
    for methods in spec['paths'].values():
        for method,op in methods.items():
            if method!='get' and (not any(p['name']=='Idempotency-Key' for p in op.get('parameters',[])) or op['operationId']=='workspace.import'):
                policy=op['x-retry-policy'];retries.append([op['operationId'],policy['effect'],policy['mode'],policy['result_check']])
    gen['retry-policies']=r.table(['操作','種別','方式','結果不明時の確認'],retries)
    blocks=[]
    for q in samples:
        request=q['method']+' '+q['url']+' HTTP/1.1\nHost: api.example.invalid\n'+'\n'.join(k+': '+str(v) for k,v in q['headers'].items())
        if 'body_base64' in q:request+='\n\n[binary: base64 decode]\n'+q['body_base64']
        if 'body' in q:request+='\n\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)
        response='HTTP/1.1 '+str(q['status'])+'\n'+'\n'.join(k+': '+str(v) for k,v in q['response_headers'].items())+'\n\n'+(('[binary: base64 decode]\n'+q['response_base64']) if 'response_base64' in q else json.dumps(q['response'],ensure_ascii=False,indent=2))
        blocks.append('<h2 id="example-'+r.e(q['id'])+'">'+r.e(q['title'])+'</h2><p>'+r.e(q.get('notes',''))+'</p>'+r.code(request,'http')+r.code(response,'http'))
    gen['http-examples']='\n'.join(blocks)
    out={};search=[]
    for page in c['pages']:
        name=page['slug']
        if name=='api':body=r.reference(spec,inv)
        else:
            raw=(SOURCE/'pages'/f'{name}.md').read_text(encoding='utf-8')
            body=r.markdown(raw,gen)
            custom=SOURCE/'pages'/f'{name}.html'
            if custom.exists():body=custom.read_text(encoding='utf-8')
            md=raw.replace('<!-- generated:coverage -->',f"API {len(inv['routes'])} operations / OpenAPI {inv['openapi_route_count']} operations / MCP {len(mcp['tools'])} import tools")
            md=md.replace('<!-- generated:figure-connection -->',(SOURCE/'figures/connection.txt').read_text(encoding='utf-8').strip())
            md=md.replace('<!-- generated:http-examples -->','\n\n'.join('## '+q['title']+'\n\n```json\n'+json.dumps(q,ensure_ascii=False,indent=2)+'\n```' for q in samples))
            md=md.replace('<!-- generated:retry-policies -->',r.md_table(['操作','種別','方式','結果不明時の確認'],retries))
            md=md.replace('<!-- generated:mcp-tools -->','```json\n'+json.dumps(mcp,ensure_ascii=False,indent=2)+'\n```')
            md=md.replace('<!-- generated:error-codes -->',r.md_table(['HTTP','code','意味と対応'],[[q[0],'`'+q[1]+'`',q[2]] for q in r.error_rows(spec)]))
            md=re.sub(r'\{\{([^}]+)\}\}',r'[\1]',md)
            md=re.sub(r'\]\(([^)]+)\)',lambda m:']('+text_link(m[1],c)+')',md)
            out[f'{vp}/guide/{name}.md']=md.encode('utf-8')
        search.append(r.search_entry(c,page,body,spec if name=='api' else None,inv))
        out[f'{vp}/{name}.html']=r.wrap(c,page,body).encode('utf-8')
    for old,new in c['redirects'].items():
        title=next(p['title'] for p in c['pages'] if p['slug']==new)
        out[f'{vp}/{old}.html']=('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ページを移動しました | Claudia Partner Docs</title><meta http-equiv="refresh" content="0; url='+new+'.html"><link rel="canonical" href="'+c['base_url']+vp+'/'+new+'.html"><body><p>このページは、<a href="'+new+'.html">'+r.e(title)+'</a>に移動しました。</p></body></html>').encode('utf-8')
    out[f'{vp}/search-index.json']=json.dumps({'format':1,'entries':search},ensure_ascii=False,separators=(',',':')).encode('utf-8')
    # The original home DOM is retained. Only its description and last link label change.
    root_body=f'<h1>Claudia Partner Docs</h1><p>Claudia Partner基盤のAPI・MCP公開ドキュメントです。基盤の考え方、接続の手順、仕様、対応状況を確認できます。利用中のAPIに対応する版を選んでください。</p><h2>公開中のドキュメント</h2><p><a href="{vp}/index.html">{r.e(c["version"])} の利用ガイド</a></p><p><a href="{vp}/api.html">APIリファレンス</a> · <a href="{vp}/mcp.html">AIエージェント・MCP</a> · <a href="links.json">アプリ向けリンク定義</a></p>'
    out['index.html']=r.wrap(c,c['pages'][0],root_body,root=True).encode('utf-8')
    for n in ['openapi.json','api-inventory.json','mcp-tools.json','examples/public-requests.json']:
        out[f'{vp}/{n}']=(ROOT/vp/n).read_bytes()
    provenance=r.read_json(ROOT/vp/'provenance.json')
    assert provenance['documentation_revision']==c['revision']
    provenance['public_openapi_sha256']=r.sha(out[f'{vp}/openapi.json'])
    out[f'{vp}/provenance.json']=r.json_bytes(provenance)
    out['links.json']=r.json_bytes({'format':1,'default_version':vp,'versions':{vp:{'api_version':c['version'],'links':{p['slug']:c['base_url']+vp+'/'+p['slug']+'.html' for p in c['pages']}|{old:c['base_url']+vp+'/'+old+'.html' for old in c['redirects']}|{n:c['base_url']+vp+'/'+n+'.json' for n in ['openapi','mcp-tools','api-inventory','provenance']}|{'examples_json':c['base_url']+vp+'/examples/public-requests.json'}}}})
    out['llms.txt']=('# Claudia Partner Docs\n\nPublic documentation for API '+c['version']+'. Documentation revision 11, pinned contract 2026-10-07. Runtime version and enabled features depend on the environment. MCP client 1.0.1 defines 8 import tools; all-service MCP is preparing. Examples are synthetic and have not been executed against customer environments.\n\n'+'\n'.join('- ['+p['title']+']('+c['base_url']+vp+('/openapi.json' if p['slug']=='api' else '/guide/'+p['slug']+'.md')+')' for p in c['pages'])+'\n').encode('utf-8')
    out['README.md']='''# Claudia Partner Docs

Claudia Partnerの顧客アプリ開発者向け公開ドキュメントです。

https://mxd2024.github.io/claudia-partner-docs/

API 0.7.0-experimental、文書改訂11（2026-10-08）、固定契約2026-10-07を対象にします。文書の最新版は接続先の稼働版を意味しません。134操作、MCPクライアント1.0.1の8ツールを記載し、有効化・権限・実機確認範囲は利用環境ごとに区別します。

## 更新とビルド

`content-source/pages/`を編集し、`python tools/build_content.py`で配信用HTML、Markdown、検索索引、manifestを生成します。`tools/public_renderer.py`は元サイトの描画処理です。スタイル・JavaScript・ロゴ・図の座標を更新する処理はありません。機械仕様は既存の`v0.7/*.json`、出典は`v0.7/provenance.json`、対象版は`content-source/site.json`にあります。`python tools/build_content.py --check`と`python tools/verify_content.py`で生成結果・リンク・仕様・元の視覚構造を確認できます。

GitHub Pagesはmainのルートを公開します。文書更新はPRでレビューし、main反映後にPagesの完了と公開URLを確認します。新しいVPS・Docker・API実行機能・認証画面は設けません。

## ファイルの整合

manifest.jsonの`files`に配信ファイルのSHA-256を記載します。`source_openapi_sha256`は公開用加工前の固定仕様の値です。公開用OpenAPIとは値が異なります。`v0.7/provenance.json`に対象版の出典と確認範囲を記載します。

## 誤記・質問

[公開Issues](https://github.com/mxd2024/claudia-partner-docs/issues)へお寄せください。顧客の名前・実データ・実際の接続先・資格は投稿しないでください。非公開情報が必要な相談は、利用環境で定められた連絡方法に従います。
'''.encode('utf-8')
    # Existing public examples, 404, robots, sitemap and visual assets remain byte-for-byte.
    previous=r.read_json(ROOT/'manifest.json')
    for name in previous['files']:
        if name not in out:out[name]=(ROOT/name).read_bytes()
    manifest={'format':1,'kind':'public-api-documentation','version':c['version'],'version_path':vp,'updated':c['updated'],'documentation_revision':c['revision'],'public_base_url':c['base_url'],'source_openapi_sha256':c['source_api_sha256'],'files':{n:r.sha(b) for n,b in sorted(out.items())}}
    out['manifest.json']=r.json_bytes(manifest)
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,expected in ASSETS.items():assert r.sha((ROOT/name).read_bytes())==expected,'Original asset changed: '+name
    out=outputs()
    if args.check:
        stale=[n for n,b in out.items() if not (ROOT/n).exists() or (ROOT/n).read_bytes()!=b]
        assert not stale,'Generated files are stale: '+', '.join(stale)
    else:
        for name,b in out.items():
            if name in ASSETS:continue
            p=ROOT/name;assert p.resolve().is_relative_to(ROOT) and not p.is_symlink()
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    print(json.dumps({'passed':True,'check_only':args.check,'public_files':len(out)-1,'assets_unchanged':list(ASSETS)}))

if __name__=='__main__':main()
