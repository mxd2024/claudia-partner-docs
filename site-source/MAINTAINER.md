# 編集・生成・公開

GitHub Pages は既存の main / ルート配信を使用する。新規サーバーや秘密は不要。

1. `v0.7/guide/*.md` と `site-source/` を編集する。
2. `python tools/build_site.py` でHTML、機能別API、検索、リンク、sitemap、manifestを生成する。
3. `python tools/verify_site.py` でリンク・アンカー・契約数・公開範囲・SHAを検査する。
4. `python -m http.server 8765 --bind 127.0.0.1` でPC／スマートフォン表示・検索・キーボードを確認する。
5. draft PRで固定commitと検証結果を提示する。公開依頼に従いレビュー後mainへ反映し、Pagesの完了と匿名HTTPSのmanifest／版を確認する。

静的ホスティングへ配備するZIPは `python tools/package_site.py --output /absolute/path/claudia-help-rev11.zip` で作る。manifestの公開ファイルだけを収録する。ZIPの中身（index.htmlとv0.7等）を指定されたdocument rootへ置く。配置先が判明するまでは既存ファイルを削除・上書きしない。

## 生成元からの移行

旧版の生成元はインフラ文書専用枝の `docs/public-site` / `tools/public-docs.py`、固定commit `a74d5a77afbfbb41d8aeb557c0e547ced46c9ed7`。そのMarkdownは改訂10の公開配布版から引き継いだ。`tools/contract_renderer.py` は同commitの公開レンダリング関数を再利用したもの。インフラ・BFF・MCPの実装／設定は変更しない。

本改訂以降、**サイト編集元はこの公開repoに置く**。旧生成器のstageはHTMLとREADMEを上書きするため、使用しない。インフラ契約を更新するときは、レビュー済みの固定版から公開加工済み `openapi.json` / `api-inventory.json` / `mcp-tools.json` / 合成例を明示取り込みし、`site-source/site.json` のAPI版・対象日・公開ファイルSHAを更新して本生成器を実行する。HTMLは毎回全体を再生成するため、手編集は不要。サイト用ソースと生成物を同じPRで更新する。

## バージョンと対象範囲

文書対象は API 0.7.0-experimental、2026-10-04契約スナップショット。実サービスの現在版・配備commit・実機疎通は保証しない。API／MCP／画像の状態は版付きの案内として記載する。新しい版は新ディレクトリを追加して旧版を残す。`manifest.json` はサイト公開対象のSHAを収録し、編集用スクリプトを対象に含めない。

## カスタムドメイン

claudia-help.meta-xdesign.com は確認時、別サーバーのAレコードを指していた。ユーザー設定済みの向き先を保持する。現在のサーバーへ既存の配備方法でファイルを配置する。GitHub PagesへのDNS付け替えを勝手に行わない。新credential発行、Cloudflareへの永続アクセス追加、セキュリティ変更はこのサイト公開に含めない。設定後はDNSの向き先、HTTPS証明書、実URL、canonical／sitemap／linksとmanifest SHAの一致を確認する。
