"""Build and check the Chat Note pages under chat-note/, with the same look as the API docs.

The API docs (v0.7/, index.html, manifest.json) are not read or written here, except that the
pages link to the shared visual assets in v0.7/ and to the documentation terms.
  python tools/build_chat_note.py           # write chat-note/
  python tools/build_chat_note.py --check   # fail if chat-note/ is stale or a check fails
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import argparse, json, posixpath, re
import public_renderer as r

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'content-source' / 'chat-note'
ASSET = '../v0.7/'
# Words that must not reach these public, generic pages (customer, environment or internal names).
BLOCKED = ['chatnote-0101', 'claudia-partner.com', 'hub-spa', 'NodeBB', 'nodebb', 'VPS', 'tanto',
           'cp-test1', '9999', 'Codex', 'Astra', 'HQ', 'CHATNOTE_', 'cf-connecting-ip', '_uid',
           'master', '提供者', '開発者', '環境管理者', 'あなたのアプリ', 'お客様専用アプリ']


def wrap(c, page, body):
    nav = []; previous = None
    for p in c['pages']:
        if p['section'] != previous: nav.append(f'<p class="nav-label">{r.e(p["section"])}</p>'); previous = p['section']
        nav.append(f'<a href="{p["slug"]}.html"' + (' aria-current="page"' if p['slug'] == page['slug'] else '') + f'>{r.e(p["title"])}</a>')
    nav.append(f'<p class="nav-label">関連</p><a class="machine" href="../index.html">基盤のAPI・認証のドキュメント</a><a class="legal" href="{ASSET}terms.html">利用条件・免責事項</a>')
    search = '<form class="site-search" role="search" onsubmit="return false"><label for="site-search">Chat Note のドキュメントを検索</label><input type="search" id="site-search" placeholder="例：サインイン、添付、案件" autocomplete="off" data-index="search-index.json" aria-controls="search-results"><div id="search-results" role="region" aria-live="polite" hidden></div></form>'
    body = body.replace('</h1>', '</h1>' + r.page_toc(body), 1) + next_links(c, page)
    label = f'{c["label"]} 改訂{c["revision"]}'
    crumb = f'<a href="index.html">Chat Note</a><span>/</span><span>{r.e(page["section"])}</span><span>/</span><span>{r.e(page["title"])}</span>'
    description = 'Claudia Partner Chat Note の使い方、見られる場所のしくみ、アプリへのはめ込みとサーバーから使う API。'
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{r.e(page['title'])} | Claudia Partner Chat Note Docs</title><meta name="description" content="{description}"><meta name="theme-color" content="#004d58"><link rel="canonical" href="{r.e(c['base_url'] + c['path'] + '/' + page['slug'] + '.html')}"><link rel="icon" href="{ASSET}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{ASSET}style.css"><link rel="stylesheet" href="{ASSET}brand.css"><script src="{ASSET}app.js" defer></script></head>
<body><a class="skip" href="#main">本文へ移動</a><header class="topbar"><a class="brand cp-brand" href="index.html"><img class="cp-brand__mark" src="{ASSET}claudia-partner-mark.svg" alt=""><span class="cp-brand__text"><span class="cp-brand__name">Claudia <span class="cp-brand__partner">Partner</span><sup class="cp-brand__trademark" style="font-size:.7em">™</sup></span><span class="cp-brand__descriptor">Chat Note Docs</span></span></a><span class="top-note">Chat Note ドキュメント</span><span class="version">{r.e(label)}</span><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">メニュー</button></header>
<div class="layout"><nav class="sidebar" id="navigation" aria-label="ドキュメント">{search}{''.join(nav)}<div class="nav-foot">公開ドキュメント<br>{r.e(label)}<br>更新 {r.e(c['updated'])}</div></nav><main id="main"><div class="breadcrumb">{crumb}</div><p class="eyebrow">{r.e(page['section'])}</p>{body}<footer class="page-foot"><span>{r.e(label)}</span><span>更新 {r.e(c['updated'])}</span><a href="guide/{page['slug']}.md">機械・テキスト向け</a><a class="legal" href="{ASSET}terms.html">利用条件・免責事項</a><span class="copyright">{r.e(c['copyright'])}</span></footer></main></div></body></html>'''


def next_links(c, page):
    by_slug = {p['slug']: p for p in c['pages']}
    targets = [n for n in dict.fromkeys(page.get('next', [])) if n != page['slug']]
    if not targets: return ''
    items = ''.join(f'<li><a href="{n}.html"><b>{r.e(by_slug[n]["title"])}</b><span>{r.e(by_slug[n]["summary"])}</span></a></li>' for n in targets)
    return f'<nav class="page-next" aria-label="次に読む"><h2 class="next-title">次に読む</h2><ul>{items}</ul></nav>'


def md_link(link, slugs):
    m = re.fullmatch(r'([a-z0-9-]+)\.html(#.*)?', link)
    if m and m[1] in slugs and not m[2]: return m[1] + '.md'
    if urlsplit(link).scheme or link.startswith('#'): return link
    return '../' + link


def outputs():
    c = r.read_json(SOURCE / 'site.json'); base = c['path'] + '/'
    slugs = [p['slug'] for p in c['pages']]
    figure = (SOURCE / 'figures/overview.html').read_text(encoding='utf-8').strip()
    out = {}; search = []
    for page in c['pages']:
        raw = (SOURCE / 'pages' / f'{page["slug"]}.md').read_text(encoding='utf-8')
        body = r.markdown(raw, {'figure-overview': figure})
        search.append(r.search_entry(c, page, body, None, None))
        out[base + page['slug'] + '.html'] = wrap(c, page, body).encode('utf-8')
        md = raw.replace('<!-- generated:figure-overview -->', r.plain(figure))
        md = re.sub(r'\]\(([^)]+)\)', lambda m: '](' + md_link(m[1], slugs) + ')', md)
        out[base + 'guide/' + page['slug'] + '.md'] = md.encode('utf-8')
    out[base + 'search-index.json'] = json.dumps({'format': 1, 'entries': search}, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    out[base + 'manifest.json'] = r.json_bytes({'format': 1, 'kind': 'chat-note-documentation', 'revision': c['revision'], 'updated': c['updated'],
                                                'public_base_url': c['base_url'] + base, 'files': {n: r.sha(b) for n, b in sorted(out.items())}})
    return c, out


def checks(c, out):
    failures = []; base = c['base_url']
    for name, raw in out.items():
        text = raw.decode('utf-8')
        for word in BLOCKED:
            if word in text: failures.append(f'blocked word {word!r} in {name}')
        for address in re.findall(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+\.[A-Za-z]{2,}', text):
            if not address.rsplit('@', 1)[1].lower().endswith(('.invalid', 'example.com')): failures.append('email in ' + name)
        if name.endswith('.html'):
            ids = set(re.findall(r'\sid="([^"]+)"', text))
            for link in re.findall(r'(?:href|src|data-index)="([^"]+)"', text):
                url = urljoin(base + name, link)
                if not url.startswith(base): continue
                p = urlsplit(url); target = unquote(p.path[len(urlsplit(base).path):]) or 'index.html'
                exists = target in out or (ROOT / target).is_file()
                if not exists: failures.append(f'link {name} -> {link}')
                elif p.fragment and target == name and p.fragment not in ids: failures.append(f'anchor {name} -> {link}')
        if name.endswith('.md'):
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if urlsplit(link).scheme or link.startswith('#'): continue
                target = posixpath.normpath((Path(name).parent / urlsplit(link).path).as_posix())
                if target not in out and not (ROOT / target).is_file(): failures.append(f'Markdown link {name} -> {link}')
    return failures


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); args = ap.parse_args()
    c, out = outputs(); failures = checks(c, out)
    if args.check:
        failures += ['stale ' + n for n, b in out.items() if not (ROOT / n).is_file() or (ROOT / n).read_bytes() != b]
        listed = {p.relative_to(ROOT).as_posix() for p in (ROOT / c['path']).rglob('*') if p.is_file()}
        failures += ['unexpected ' + n for n in sorted(listed - set(out))]
    elif not failures:
        for name, raw in out.items():
            p = ROOT / name; assert p.resolve().is_relative_to(ROOT / c['path']) and not p.is_symlink()
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
    print(json.dumps({'passed': not failures, 'check_only': args.check, 'files': len(out), 'pages': len(c['pages']), 'failures': failures}, ensure_ascii=False, indent=2))
    assert not failures


if __name__ == '__main__': main()
