"""Check the GitHub-first document entry and migration requirements, without runtime claims."""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'site-source/site.json').read_bytes())
readme=(ROOT/'README.md').read_text(encoding='utf-8')
def guide(name): return (ROOT/'v0.7/guide'/f'{name}.md').read_text(encoding='utf-8')
assert f"文書改訂{config['revision']}" in readme
entry=['index','versions','request-access','app-architecture','quickstart','authentication','service-access','mcp','tables','media','reliability','sample-app','examples','support','changelog','specs']
for name in entry: assert f'(v0.7/guide/{name}.md)' in readme,name
for name in ['openapi.json','api-inventory.json','mcp-tools.json','provenance.json']:
 assert f'(v0.7/{name})' in readme,name
assert '静的配備は必須ではありません' in readme
assert 'https://github.com/mxd2024/claudia-partner-docs/issues' in readme
app=guide('app-architecture'); access=guide('request-access'); versions=guide('versions'); support=guide('support')
for text in ['Macで開発し、VPSへ移す設計','同じアプリコード・認証方式','併存登録','[準備中]','[環境による]','公開の認証局','SSH転送や独自の認証局の登録を要求しません','設定の差分','Cookie','秘密の参照先','開発用戻り先の登録を削除・失効','正本・実機受入の確認待ち']:
 assert text in app,text
for text in ['本番の固定HTTPS redirect_uri','併存希望と期間','開発URI削除予定日','実値は非公開','公開CAのHTTPS入口']:
 assert text in access,text
assert '開発・本番redirect_uriの併存登録とMac→VPS移行 | [準備中]' in versions
for text in ['追加','新しいIssue','顧客名・個人情報','回答時間や24時間対応は保証していません']:
 assert text in support,text
all_md=list((ROOT/'v0.7/guide').glob('*.md'))+[ROOT/'README.md']
for path in all_md:
 text=path.read_text(encoding='utf-8')
 assert 'https://mxd2024.github.io/claudia-partner-docs/' not in text, ('older deployed-site link',path.name)
 assert not re.search(r'5分|dot|24時間対応を保証します',text),('internal operations or response promise',path.name)
 for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
  if link.startswith('https:'): continue
  target=(path.parent/link.split('#')[0]).resolve()
  assert target.is_relative_to(ROOT) and target.is_file(), (path.name,link)
result={'passed':True,'documentation_revision':config['revision'],'readme_guide_entries':len(entry),'markdown_files_checked':len(all_md),
 'github_relative_navigation':True,'no_older_deployed_site_links':True,'design_and_availability_distinguished':True,
 'migration_and_development_redirect_retirement_documented':True,'public_issue_instructions_present':True,
 'no_internal_monitoring_details_or_response_time_promise':True,'runtime_development_route_verified':False}
(ROOT/'.qa/github-entry-report.json').write_bytes(json.dumps(result,ensure_ascii=False,indent=2).encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
