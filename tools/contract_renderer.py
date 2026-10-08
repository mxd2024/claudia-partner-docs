"""Build, verify and stage the deliberately selected public API documentation."""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/public-site'
PUBLIC_REMOTE = 'https://github.com/mxd2024/claudia-partner-docs.git'
GROUPS = {
    'business': '業務・本人情報', 'tables': '顧客定義表 v1', 'workspaces': '業務表・ケース v2',
    'workspace-sockets': '関連・所属', 'workspace-access': '人物・行アクセス',
    'assets': '資産', 'media': '画像・添付', 'service-access': 'サービス・権限',
    'apps': 'アプリ管理', 'app-packages': 'アプリ定義・移行', 'organization': '組織管理',
    'identity': 'セッション', 'health': '稼働確認',
}
e = html.escape
STATUS_CLASS = {'提供中': 'ok', '準備中': 'soon', '未提供': 'none', '環境による': 'env'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def slug(value):
    return re.sub(r'[^a-zA-Z0-9_-]', '-', value)


def inline(text):
    # Content is authored locally, escaped first, then only this limited markup is emitted.
    text = e(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\{\{(提供中|準備中|未提供|環境による)\}\}', lambda m: f'<span class="status status-{STATUS_CLASS[m[1]]}">{m[1]}</span>', text)
    def link(match):
        url = html.unescape(match[2])
        assert not urlsplit(url).scheme or urlsplit(url).scheme == 'https', url
        return f'<a href="{e(url, quote=True)}">{match[1]}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)


def code(value, language='json', schema_links=False):
    text = e(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2))
    if schema_links:
        text = re.sub(r'#/components/schemas/([A-Za-z0-9_-]+)',
                      lambda m: f'<a href="#schema-{m[1]}">{m[0]}</a>', text)
    return f'<pre><span class="code-label">{e(language)}</span><code>{text}</code></pre>'


def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def markdown(text, generated):
    lines = text.splitlines(); result = []; i = 0; heading = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        if line.startswith('<!-- generated:'):
            key = line.removeprefix('<!-- generated:').removesuffix(' -->')
            assert key in generated, key
            result.append(generated[key]); i += 1; continue
        if line.startswith('```'):
            lang = line[3:]; body = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                body.append(lines[i]); i += 1
            assert i < len(lines), 'Unclosed code fence'
            result.append(code('\n'.join(body), lang)); i += 1; continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#')); title = line[level:].strip(); heading += 1
            result.append(f'<h{level} id="section-{heading}">{inline(title)}</h{level}>'); i += 1; continue
        if line.startswith('> '):
            result.append('<blockquote><p>' + inline(line[2:]) + '</p></blockquote>'); i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells): rows.append([inline(c) for c in cells])
                i += 1
            assert len(rows) >= 2
            result.append(table(rows[0], rows[1:])); continue
        if re.match(r'(?:- |\d+\. )', line):
            ordered = bool(re.match(r'\d+\. ', line)); tag = 'ol' if ordered else 'ul'; items = []
            while i < len(lines) and re.match(r'\d+\. ' if ordered else '- ', lines[i].strip()):
                items.append('<li>' + inline(re.sub(r'^(?:- |\d+\. )', '', lines[i].strip())) + '</li>'); i += 1
            result.append(f'<{tag}>' + ''.join(items) + f'</{tag}>'); continue
        paragraph = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|>|\||```|<!--|- |\d+\. )', lines[i].strip()):
            paragraph.append(lines[i].strip()); i += 1
        result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(result)


def coverage(inventory, mcp):
    return '<div class="stats">' + ''.join(f'<div class="stat"><b>{count}</b><span>{label}</span></div>' for count, label in [(len(inventory['routes']), '公開API操作'), (inventory['openapi_route_count'], 'OpenAPI定義'), (len(mcp['tools']), '現行の取込MCPツール')]) + '</div>'


def schema_label(schema):
    if '$ref' in schema:
        name = schema['$ref'].split('/')[-1]
        return f'<a href="#schema-{e(name)}">{e(name)}</a>'
    return '<code>' + e(schema.get('type', 'schema')) + '</code>'


AVAILABILITY = {'implemented; deployment-specific': '提供中（環境による）', 'implemented; fixed health endpoint': '提供中'}
RATE_LIMITS = {
    '固定rpmは本契約では未確定。配備側の制限と429を確認する。': '固定のレート上限は定めていません。環境側の制限があり、429が返ることがあります。',
    'モジュール内の同時2要求。固定rpmは未設定。上流の制限は環境設定による。': '同時2要求まで。固定のレート上限は定めていません。環境側の制限があり、429が返ることがあります。',
    'Coreのhealth専用レート制限はなし。上流proxyの制限は配備設定による。': 'この確認用のルートに、専用のレート制限はありません。環境側の制限はあります。',
}
SERVER_DESCRIPTION = '末尾スラッシュなしの、基盤のHTTPS origin。アプリや認証サービスのURLとは別。'


def public_availability(value):
    if value in AVAILABILITY: return AVAILABILITY[value]
    if value.startswith('experimental'): return '試験提供（環境による）'
    return '環境による'

HTTP_ACTIONS = {
    400: 'APIの型・必須項目を確認する', 401: '認証を更新する、または再ログインする', 403: '現在の権限とMFAを確認する',
    404: '対象の存在と権限を確認する（隠された対象を推測しない）', 409: '状態を再取得し、同じ操作の結果を確認する',
    412: '再取得し、差分を確認してから、操作を決め直す', 413: '入力やファイルを訂正する', 415: '入力やファイルを訂正する', 422: '入力やファイルを訂正する',
    428: '必須の条件（版・理由・再送キー）を付ける', 429: '`Retry-After`に従い、間隔を空けて再試行する',
    500: '`request_id`を記録する。結果を確認する前に、別の操作を再送しない', 503: '`request_id`を記録する。結果を確認する前に、別の操作を再送しない',
    507: '環境管理者に、容量と保持の方針を確認する',
}
CODE_NOTES = {
    'CURSOR_STALE': '一覧が変わり、`cursor`が使えません。蓄積したページを捨てて、最初から検索し直す',
    'VERSION_CONFLICT': '期待した版と現在の版が一致しません。再取得し、差分を確認してから、操作を決め直す',
    'OUTCOME_UNKNOWN': '操作が完了したか確認できません。同じキーと本文で結果を確認する。別のキーで再実行しない',
    'TOKEN_INVALID': 'トークンが無効です。ログイン直後は反映待ちのことがあります。待機枠で再確認し、続くときは再ログインする',
    'TOKEN_EXPIRED': 'トークンの期限が切れています。更新または再ログインする',
    'MFA_REQUIRED': 'MFAを完了した認証が必要です。ログインの手順を、最初からやり直す（トークンの更新では代用できない）',
    'REAUTH_REQUIRED': '再認証が必要です。ログインの手順を、最初からやり直す（トークンの更新では代用できない）',
    'AI_MUST_USE_PROPOSALS': 'AIによる直接の更新は、許可されていません。承認された提案の経路が必要です。利用者の資格に付け替えて、回避しない。現在、公開APIで提案を作る手段はありません',
    'AI_SUSPENDED': 'AIの主体、委任、方針などが、現在、使えません。停止や期限を、管理側で確認し、同じ要求を、繰り返さない',
    'AI_RATE_LIMITED': 'AIの操作の、割当の上限です。示された待機の条件に従い、並列化や別の主体で、回避しない',
    'PROPOSAL_CONFLICT': '提案が前提にした行の版と、現在の版が一致しません。最新の状態と提案の内容を確認し直す',
    'IDEMPOTENCY_IN_PROGRESS': '同じキーの操作が処理中です。待ってから、同じキーで結果を確認する',
    'IDEMPOTENCY_MISMATCH': '同じキーで、本文を変えて送っています。本文を元に戻して再送するか、状態を確認してから、新しいキーで送る',
    'ASSET_IDEMPOTENCY_MISMATCH': '同じキーで、本文を変えて送っています。本文を元に戻して再送するか、状態を確認してから、新しいキーで送る',
}


def error_action(code, status):
    return CODE_NOTES.get(code) or HTTP_ACTIONS.get(status, '対象の操作の応答と合わせて確認する')


def error_rows(spec):
    return [[str(value), key, error_action(key, value)] for key, value in sorted(spec['x-error-status'].items(), key=lambda item: (item[1], item[0]))]


def md_table(headers, rows):
    esc = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] + ['| ' + ' | '.join(esc(c) for c in row) + ' |' for row in rows])


def text_link(config, vp, link):
    """In the text (Markdown) version, a link to another page goes to that page's text version."""
    m = re.fullmatch(r'([a-z0-9-]+)\.html(#.*)?', link)
    base = config['base_url'] + vp + '/'
    if m and m[1] == 'api': return base + 'openapi.json'
    if m and any(p['slug'] == m[1] for p in config['pages']): return base + 'guide/' + m[1] + '.md'
    return urljoin(base, link)


def public_text(value):
    value = value.replace('案件', 'ケース')
    value = value.replace('design-images', 'sample-files').replace('design-blue.png', 'sample-image.png').replace('デザイン原本', '参考画像').replace('デザイン見本', '参考画像')
    value = value.replace('稼働サイト', '提供環境').replace('配備側', '環境側').replace('配備', '環境').replace('有効モジュール', '有効な機能').replace('モジュール', '機能')
    return re.sub(r'Core(?![A-Za-z])', '基盤', value)


def publicize(node):
    if isinstance(node, dict):
        return {k: publicize(v) for k, v in node.items()}
    if isinstance(node, list):
        return [publicize(v) for v in node]
    if isinstance(node, str):
        return RATE_LIMITS.get(node) or public_text(node)
    return node


def public_spec(spec):
    """Publish-time view of the contract: customer-facing wording only; the source of truth is unchanged."""
    for methods in spec['paths'].values():
        for op in methods.values():
            op['x-availability'] = public_availability(op['x-availability'])
            op.get('x-required-authority', {}).pop('client_ids', None)
    spec['servers'][0]['variables']['baseUrl']['description'] = SERVER_DESCRIPTION
    for schema in spec['components']['schemas'].values():
        props = schema.get('properties') if isinstance(schema, dict) else None
        if props and isinstance(props.get('id'), dict) and 'expected_actor' in str(props['id'].get('description', '')):
            props['id']['description'] = '対象の行のid'
    spec['x-availability-legend'] = {
        '提供中': '提供しています。環境での有効化と、権限は必要です。',
        '試験提供': '試験の段階です。仕様は変更されることがあります。利用する版を固定してください。',
        '環境による': '環境ごとに有効かどうかが異なります。環境管理者に確認してください。',
    }
    return publicize(spec)


def reference(spec, inventory):
    rows = inventory['routes']
    out = ['<h1>APIリファレンス</h1><p>パス・操作ID・機能名で検索できます。各操作を開くと、認証、入力、応答を確認できます。実装に存在する操作でも、利用中の環境での有効化と権限が必要です。</p>',
           f'<div class="notice">全{len(rows)}操作にOpenAPI定義があります。API仕様の掲載は、全操作のMCP提供済みを意味しません。</div>',
           '<p><a href="openapi.json">OpenAPI JSON</a> · <a href="api-inventory.json">全API一覧 JSON</a> · <a href="#schemas">共通データ型</a></p>',
           '<div class="filters"><label>操作を検索<input type="search" id="api-search" placeholder="例：media、query、権限" autocomplete="off"></label><label>機能<select id="api-group"><option value="">すべての機能</option>' + ''.join(f'<option value="{g}">{e(label)}</option>' for g, label in GROUPS.items()) + f'</select></label><button type="button" id="clear-search">クリア</button></div><p id="result-count" role="status" aria-live="polite">{len(rows)} / {len(rows)} 操作を表示</p><p id="empty-result" class="empty" hidden>一致する操作はありません。条件を変更してください。</p>']
    for route in rows:
        op = spec['paths'].get(route['path'], {}).get(route['method'].lower())
        group = GROUPS[route['group']]; identity = 'op-' + slug(route['operation_id'])
        state = 'OpenAPI定義あり' if op else '機械仕様 準備中'
        badge = 'badge' if op else 'badge pending'
        search = ' '.join([route['method'], route['path'], route['operation_id'], group, route['group'], (op or {}).get('summary','')]).lower()
        out.append(f'<details class="operation" id="{identity}" data-group="{e(route["group"])}" data-search="{e(search, quote=True)}"><summary><span class="method {route["method"].lower()}">{route["method"]}</span><span class="route">{e(route["path"])}</span><span class="opmeta">{e(group)} · {e(route["operation_id"])}</span></summary><div class="opbody">')
        out.append(f'<p><span class="{badge}">{state}</span><a class="anchor-link" href="#{identity}">この操作へのリンク</a></p>')
        if not op:
            out.append('<p>ルートは実装に存在しますが、入力・応答の機械仕様は整備中です。呼出し条件を推測して利用せず、提供環境の管理者へ確認してください。</p></div></details>'); continue
        out.append('<h3>' + e(op.get('summary', route['operation_id'])) + '</h3>')
        out.append('<p>' + e(op.get('description', '現在の認証・認可に従って実行します。')) + '</p>')
        out.append('<h3>認証</h3><p>' + ('Bearer JWT。主体と現在権限を確認します。' if op.get('security', spec.get('security')) else 'この定義に認証指定はありません。環境の条件も確認してください。') + '</p>')
        out.append('<h3>操作別の認可条件</h3>' + code(op.get('x-required-authority', {})))
        out.append('<h3>再送と結果確認</h3>' + code(op.get('x-retry-policy', {})))
        params = op.get('parameters', [])
        if params:
            out.append('<h3>パラメーター</h3>' + table(['名前 / 場所', '必須', '型・条件'], [[f'<code>{e(p["name"])}</code><br>{e(p["in"])}', '必須' if p.get('required') else '任意', code(p.get('schema', {}), schema_links=True) + e(p.get('description', ''))] for p in params]))
        if op.get('requestBody'):
            out.append('<h3>リクエスト本文</h3>')
            for typ, content in op['requestBody'].get('content', {}).items():
                out.append('<p><code>' + e(typ) + '</code></p>' + code(content.get('schema', {}), schema_links=True))
        out.append('<h3>応答</h3>' + table(['HTTP', '内容 / データ型'], [[f'<code>{e(status)}</code>', e(res.get('description', '')) + '<br>' + '<br>'.join(e(typ) + ' · ' + schema_label(v.get('schema', {})) for typ, v in res.get('content', {}).items())] for status, res in op.get('responses', {}).items()]))
        out.append('<p>提供条件: ' + e(op.get('x-availability', '環境による')) + '</p><p>制限: ' + e(op.get('x-rate-limit','環境に依存')) + '</p><p><a href="examples.html">完全な要求・応答と実行例</a> · <a href="principles.html">状態の読み方</a></p>')
        out.append('</div></details>')
    out.append('<h2 id="schemas">共通データ型</h2><p>各操作の$refが参照する定義です。入力に使える欄や型は、現在の表定義・認可によってさらに制限されます。</p>')
    for name, value in sorted(spec.get('components', {}).get('schemas', {}).items()):
        out.append(f'<details class="schema" id="schema-{e(name)}"><summary>{e(name)}</summary><div class="opbody">{code(value, schema_links=True)}</div></details>')
    return '\n'.join(out)


