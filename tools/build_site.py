"""Build the public developer help center from reviewed, public-only inputs."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import html
import json
import re
import sys
import contract_renderer as renderer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site-source'
CONFIG = json.loads((SOURCE / 'site.json').read_text(encoding='utf-8'))
VP = CONFIG['version_path']
VERSION = CONFIG['version']
BASE = CONFIG['base_url']
ESC = html.escape
OUT = {}
SEARCH = []
PAGES = CONFIG['pages']
GROUPS = renderer.GROUPS


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


def emit(name, content):
    OUT[name] = content.encode('utf-8') if isinstance(content, str) else content


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def plain(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def page_toc(body):
    items = re.findall(r'<h2 id="(section-\d+)">(.*?)</h2>', body)
    if len(items) < 4:
        return ''
    return '<nav class="page-toc" aria-label="このページの内容"><p class="toc-title">このページの内容</p><ol>' + ''.join(f'<li><a href="#{i}">{title}</a></li>' for i,title in items) + '</ol></nav>'


def local_links(text, markdown=False):
    # Both old distribution URLs and the new public host become portable relative links.
    for base in ['https://mxd2024.github.io/claudia-partner-docs/', BASE]:
        text = text.replace(base + VP + '/guide/', 'guide/' if markdown else '')
        text = text.replace(base + VP + '/', '')
        text = text.replace(base, '../')
    if not markdown:
        text = re.sub(r'(?<=\()([a-z0-9-]+)\.md(?=[#)])', r'\1.html', text)
        text = re.sub(r'(?<=\()guide/([a-z0-9-]+)\.md(?=[#)])', r'\1.html', text)
        text = re.sub(r'(?<=\()\.\./([a-z0-9-]+\.html)(?=[#)])', r'\1', text)
    return text


def search_box(prefix):
    return f'''<form class="site-search" role="search"><label for="site-search">ドキュメントを検索</label><div class="search-field"><span aria-hidden="true">⌕</span><input id="site-search" type="search" placeholder="例：BFF、OIDC、404、画像" autocomplete="off" data-index="{prefix}search-index.json" aria-controls="search-results"></div><div id="search-results" aria-live="polite" hidden></div></form>'''


def sidebar(prefix, active):
    parts = [search_box(prefix)]
    section = None
    for p in PAGES:
        if p['section'] != section:
            section = p['section']
            parts.append(f'<p class="nav-label">{ESC(section)}</p>')
        current = ' aria-current="page"' if active == p['slug'] else ''
        parts.append(f'<a href="{prefix}{p["slug"]}.html"{current}>{ESC(p["title"])}</a>')
    parts.append(f'<div class="nav-foot">文書対象版<br>{VERSION}<br>契約スナップショット 2026-10-04</div>')
    return ''.join(parts)


def wrap(slug, title, body, root=False, landing=False):
    prefix = VP + '/' if root else ''
    home = 'index.html' if root else '../index.html'
    canonical = BASE + (slug + '.html' if root else VP + '/' + slug + '.html')
    header = f'''<a class="brand" href="{home}"><img src="{prefix}claudia-partner-mark.svg" alt=""><span>Claudia <b>Partner</b><small>Developer Help</small></span></a><nav class="top-links" aria-label="主な分類"><a href="{prefix}guides.html">ガイド</a><a href="{prefix}api.html">API</a><a href="{prefix}releases.html">リリース情報</a></nav><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">メニュー</button>'''
    toc = page_toc(body) if not landing else ''
    footer = f'''<footer class="page-foot"><p>文書対象: <b>{VERSION}</b> · 文書改訂 {CONFIG['revision']} · 更新 {CONFIG['updated']}</p><p>契約スナップショット 2026-10-04。実環境への疎通は未確認です。<a href="{prefix}versions.html">提供条件と制約</a></p></footer>'''
    nav = search_box(prefix) if root else sidebar(prefix, slug)
    container = 'home-layout' if root else 'layout'
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{ESC(title)} | Claudia Partner 開発者ヘルプ</title><meta name="description" content="Claudia Partnerの顧客アプリ開発者向けガイド、API仕様、リリース情報。文書対象版と提供条件を確認できます。"><meta name="theme-color" content="#145c52"><link rel="canonical" href="{canonical}"><link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}style.css"><script src="{prefix}app.js" defer></script></head>
<body><a class="skip" href="#main">本文へ移動</a><header class="topbar">{header}</header><div class="version-strip">文書対象 <strong>{VERSION}</strong><span>2026-10-04契約 · 改訂{CONFIG['revision']}</span><a href="{prefix}versions.html">提供状況を確認 →</a></div><div class="{container}"><nav class="sidebar" id="navigation" aria-label="ドキュメント">{nav}</nav><main id="main"><div class="breadcrumb"><a href="{home}">開発者ヘルプ</a><span aria-hidden="true"> / </span><span>{ESC(title)}</span></div>{toc}{body}{footer}</main></div><footer class="site-foot">Claudia Partner · 顧客アプリ開発者向け公開ドキュメント</footer></body></html>'''


def page(slug, title, body, root=False, landing=False):
    name = ('' if root else VP + '/') + slug + '.html'
    emit(name, wrap(slug, title, body, root, landing))
    if not root:
        text = title if slug.startswith('api-') else plain(body)
        SEARCH.append({'t':title,'u':slug+'.html','s':'API' if slug.startswith('api') else 'ガイド','h':[], 'x':text})


def cards(items, prefix=''):
    return '<div class="cards">' + ''.join(f'<a class="card" href="{prefix}{url}"><span class="card-kicker">{ESC(kicker)}</span><h2>{ESC(title)}</h2><p>{ESC(desc)}</p><span class="card-arrow" aria-hidden="true">→</span></a>' for kicker,title,desc,url in items) + '</div>'


def build():
    spec_raw = (ROOT / VP / 'openapi.json').read_bytes()
    assert hashlib.sha256(spec_raw).hexdigest() == CONFIG['public_openapi_sha256'], 'Review and pin a changed public contract before building'
    spec = json.loads(spec_raw)
    inventory = json.loads(read(VP + '/api-inventory.json'))
    assert spec['info']['version'] == inventory['api_version'] == VERSION
    assert len(inventory['routes']) == 132
    for p in PAGES:
        source = ROOT / VP / 'guide' / (p['slug'] + '.md')
        if source.exists():
            raw = source.read_text(encoding='utf-8')
            body = renderer.markdown(local_links(raw), {})
            if p['slug'] == 'examples':
                samples = json.loads(read(VP+'/examples/public-requests.json'))
                intro = raw.split('## '+samples[0]['title'])[0]
                body = renderer.markdown(local_links(intro), {})
                for sample in samples:
                    headers = '\n'.join(k+': '+str(v) for k,v in sample['headers'].items())
                    request = sample['method']+' '+sample['url']+' HTTP/1.1\nHost: api.example.invalid\n'+headers
                    if 'body_base64' in sample: request+='\n\n[binary: base64 decode]\n'+sample['body_base64']
                    if 'body' in sample: request+='\n\n'+json.dumps(sample['body'],ensure_ascii=False,indent=2)
                    response = 'HTTP/1.1 '+str(sample['status'])+'\n'+'\n'.join(k+': '+str(v) for k,v in sample['response_headers'].items())+'\n\n'
                    response += '[binary: base64 decode]\n'+sample['response_base64'] if 'response_base64' in sample else json.dumps(sample['response'],ensure_ascii=False,indent=2)
                    body += '<h2 id="example-'+ESC(sample['id'])+'">'+ESC(sample['title'])+'</h2><p>'+ESC(sample.get('notes',''))+'</p>'+renderer.code(request,'http')+renderer.code(response,'http')
            page(p['slug'], p['title'], body)

    hero = '''<section class="hero"><p class="eyebrow">CLAUDIA PARTNER / DEVELOPERS</p><h1>業務に合うアプリを、<br>共通APIから。</h1><p class="lead">全体像を知り、最初のデータを読む。<br>ガイド・API仕様・リリース情報をここから探せます。</p><div class="hero-actions"><a class="button" href="v0.7/quickstart.html">開発を始める <span aria-hidden="true">→</span></a><a href="v0.7/index.html">まず全体像を読む</a></div></section>'''
    home = hero + cards([
        ('01 / LEARN','ガイド','接続準備、認証、表と行、メディア、MCP。目的に沿って学びます。','guides.html'),
        ('02 / BUILD','APIリファレンス','132操作の入力・応答・認可条件。機能ごとに仕様を確認します。','api.html'),
        ('03 / FOLLOW','リリース情報','文書対象版、提供条件、変更履歴と旧版を確認します。','releases.html')], VP + '/')
    home += '''<section class="start-section"><p class="eyebrow">FIRST STEPS</p><h2>最初の接続までの3ステップ</h2><div class="steps"><a href="v0.7/index.html"><b>1</b><span>構成を理解する<small>顧客アプリ・BFF・共通サービス</small></span></a><a href="v0.7/request-access.html"><b>2</b><span>接続情報をそろえる<small>対象版・有効な機能・ログイン設定</small></span></a><a href="v0.7/quickstart.html"><b>3</b><span>最初のデータを読む<small>本人確認から検証用の表へ</small></span></a></div></section>'''
    home += '''<section class="home-bottom"><div><p class="eyebrow">SAMPLE</p><h2>小さなアプリで、役割をつかむ</h2><p>架空の業務メモを例に、画面・BFF・APIのつなぎ方を確認します。</p><a href="v0.7/sample-app.html">サンプルを読む →</a></div><div class="notice"><b>この文書で確認できる範囲</b><p>API契約は提供済み。実環境への疎通は未確認です。取込MCPは対象版で8ツール、全サービスMCPは準備中です。</p><a href="v0.7/versions.html">機能ごとの状態と制約 →</a></div></section>'''
    page('index','開発者ヘルプ',home,root=True,landing=True)
    guides = '<p class="eyebrow">GUIDES</p><h1>ガイド</h1><p class="lead">最初の接続から、機能別の実装と運用まで。</p>'
    sections = {}
    for p in PAGES:
        if p['slug'] not in {'api','guides','releases'}: sections.setdefault(p['section'],[]).append(p)
    for section, pages in sections.items():
        guides += f'<section class="guide-section"><h2>{ESC(section)}</h2><div class="link-grid">'+''.join(f'<a href="{p["slug"]}.html"><b>{ESC(p["title"])}</b><span>{ESC(p["summary"])}</span><i aria-hidden="true">→</i></a>' for p in pages)+'</div></section>'
    page('guides','ガイド',guides,landing=True)

    # Keep the reviewed renderer and contract unchanged; split its output by feature.
    full = renderer.reference(spec, inventory)
    operations = re.findall(r'<details class="operation".*?</details>', full, re.S)
    assert len(operations) == 132
    by_group = {g:[] for g in GROUPS}
    rows = []
    for route, card in zip(inventory['routes'], operations):
        group = route['group']
        identity = 'op-' + renderer.slug(route['operation_id'])
        assert f'id="{identity}"' in card
        card = card.replace('href="#schema-', 'href="api-schemas.html#schema-')
        by_group[group].append(card)
        op = spec['paths'][route['path']][route['method'].lower()]
        url = f'api-{group}.html#{identity}'
        query = ' '.join([route['method'],route['path'],route['operation_id'],GROUPS[group],op.get('summary','')]).lower()
        rows.append(f'<div class="operation-row" id="{identity}" data-group="{group}" data-search="{ESC(query,quote=True)}" data-destination="{url}"><a href="{url}"><span class="method {route["method"].lower()}">{route["method"]}</span><code>{ESC(route["path"])}</code><span>{ESC(op.get("summary",route["operation_id"]))}</span></a></div>')
        SEARCH.append({'t':op.get('summary',route['operation_id']),'u':url,'s':GROUPS[group],'h':[],'x':query+' '+op.get('description','')})
    filters = '<div class="filters"><label for="api-search">操作を検索<input id="api-search" type="search" placeholder="例：query、media、権限"></label><label for="api-group">機能<select id="api-group"><option value="">すべての機能</option>'+''.join(f'<option value="{g}">{ESC(label)}</option>' for g,label in GROUPS.items())+'</select></label><button id="clear-search" type="button">クリア</button></div><p id="result-count" role="status" aria-live="polite">132 / 132 操作</p><p id="empty-result" hidden>一致する操作がありません。条件を変更してください。</p>'
    api = '<p class="eyebrow">API REFERENCE</p><h1>APIリファレンス</h1><p>機能ごとに詳細を開き、入力・応答・認可条件を確認します。掲載は接続先での有効化や実機動作を保証しません。</p><div class="notice">API契約: 提供済み（132操作） · 実機疎通: 未確認。<a href="quickstart.html">有効な機能の確認と404</a></div><p><a href="openapi.json">OpenAPI JSON</a> · <a href="api-inventory.json">操作一覧JSON</a> · <a href="api-schemas.html" id="schemas">共通データ型</a></p>'+filters+''.join(rows)
    # Old schema deep links remain valid and have a clickable fallback without JavaScript.
    api += '<div class="legacy-anchors">'+''.join(f'<a id="schema-{ESC(n)}" data-destination="api-schemas.html#schema-{ESC(n)}" href="api-schemas.html#schema-{ESC(n)}">{ESC(n)}</a>' for n in spec['components']['schemas'])+'</div>'
    page('api','APIリファレンス',api,landing=True)
    for group, values in by_group.items():
        page('api-'+group, GROUPS[group]+' API', f'<p class="eyebrow">API / {ESC(group.upper())}</p><h1>{ESC(GROUPS[group])}</h1><p><a href="api.html">← 全操作を検索</a> · <a href="api-schemas.html">共通データ型</a></p><p class="notice">文書対象版の契約です。実機疎通は未確認。環境での有効化・現在の権限が必要です。</p>'+''.join(values),landing=True)
    schemas = full[full.index('<h2 id="schemas">'):]
    page('api-schemas','共通データ型','<h1>共通データ型</h1><p><a href="api.html">← APIリファレンス</a></p>'+schemas,landing=True)
    release = '<p class="eyebrow">RELEASES</p><h1>リリース情報</h1><p class="lead">APIの対象版と、文書の変更を分けて確認します。</p>'+cards([
        ('STATUS','提供状況と制約','API契約・実機未確認・MCP・メディアの範囲。','versions.html'),
        ('HISTORY','変更履歴','文書改訂11の変更内容と互換性の扱い。','changelog.html'),
        ('ARCHIVE','版別ドキュメント','公開されている版と、旧版・廃止情報。','archive.html')])
    release += f'<h2>文書対象版</h2><div class="release-row"><b>{VERSION}</b><span>契約 2026-10-04 / 文書改訂{CONFIG["revision"]}</span><a href="index.html">この版のガイド →</a></div><p>このサイトの更新はAPIの配備を行いません。利用環境の対象版と有効なモジュールは環境管理者へ確認してください。</p>'
    page('releases','リリース情報',release,landing=True)
    page('archive','版別ドキュメントと旧版','<h1>版別ドキュメントと旧版</h1><p>現在公開しているAPI文書は0.7.0-experimentalです。これより前のAPI版の文書は公開されていません。</p><p><a href="index.html">v0.7のガイド</a> · <a href="api.html">v0.7のAPI</a> · <a href="changelog.html">文書の変更履歴</a></p><h2>v1 / v2というパスについて</h2><p>APIパスのv1とv2は、このv0.7契約に含まれる系列です。旧文書の版を表すものではありません。<a href="concepts.html">系列の選び方</a>を確認してください。</p><h2>今後の版</h2><p>互換性が変わる場合は別の文書版を追加し、既存の版別URLを残します。サポート期間・廃止予告期間は未確定です。</p>',landing=True)
    page('operations','サポートへの案内','<h1>サポートへの案内</h1><p><a href="support.html">サポートと窓口へ進む →</a></p>',landing=True)
    emit('404.html', '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ページが見つかりません</title><h1>ページが見つかりません</h1><p>URLと文書の版を確認してください。</p><a href="'+BASE+'">開発者ヘルプへ戻る</a></html>')
    emit(VP+'/style.css', (SOURCE/'style.css').read_bytes())
    emit(VP+'/app.js', (SOURCE/'app.js').read_bytes())
    emit(VP+'/search-index.json',json_text({'format':1,'entries':SEARCH}))
    links = json.loads(read('links.json'))
    for slug in list(links['versions'][VP]['links']):
        links['versions'][VP]['links'][slug] = links['versions'][VP]['links'][slug].replace('https://mxd2024.github.io/claudia-partner-docs/',BASE)
    for slug in ['guides','releases','sample-app','archive','api-schemas']:
        links['versions'][VP]['links'][slug] = BASE+VP+'/'+slug+'.html'
    emit('links.json',json_text(links))
    html_names = sorted(n for n in OUT if n.endswith('.html') and n != '404.html')
    emit('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+n+'</loc><lastmod>'+CONFIG['updated']+'</lastmod></url>' for n in html_names)+'</urlset>\n')
    emit('robots.txt','User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
    emit('llms.txt',f'# Claudia Partner Developer Help\n\n文書対象 {VERSION}。契約スナップショット2026-10-04、文書改訂{CONFIG["revision"]}。実環境疎通は未確認。\n\n'+''.join(f'- [{p["title"]}]({BASE}{VP}/guide/{p["slug"]}.md)\n' for p in PAGES if (ROOT/VP/'guide'/(p['slug']+'.md')).exists())+f'\n- [OpenAPI]({BASE}{VP}/openapi.json)\n- [版と制約]({BASE}{VP}/versions.html)\n')
    for name, raw in OUT.items():
        destination = ROOT / name
        assert not destination.is_symlink()
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(raw)
    # Only selected public deliverables are in the deployment manifest; never copy the repo wholesale.
    selected = sorted({'.nojekyll','404.html','index.html','links.json','llms.txt','robots.txt','sitemap.xml','README.md'} | {p.relative_to(ROOT).as_posix() for p in (ROOT/VP).rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    previous = json.loads(read('manifest.json'))
    previous.update({'updated':CONFIG['updated'],'documentation_revision':CONFIG['revision'],'public_base_url':BASE,'contract_snapshot_date':'2026-10-04','runtime_verified':False,'files':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in selected}})
    (ROOT/'manifest.json').write_bytes(json_text(previous).encode('utf-8'))
    print(json_text({'built_pages':len(html_names),'operations':len(operations),'api_index_bytes':len(OUT[VP+'/api.html']),'revision':CONFIG['revision'],'target_url':BASE}))


if __name__ == '__main__':
    build()
