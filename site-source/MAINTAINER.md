# 編集・生成・公開

GitHub Pages は既存の main / ルート配信を使用する。新規サーバーや秘密は不要。

1. `v0.7/guide/*.md` と `site-source/` を編集する。
2. `python tools/build_site.py` でHTML、機能別API、検索、リンク、sitemap、manifestを生成する。
3. `python tools/verify_site.py` でリンク・アンカー・契約数・公開範囲・SHAを検査する。
4. `python -m http.server 8765 --bind 127.0.0.1` でPC／スマートフォン表示・検索・キーボードを確認する。
5. draft PRで固定commitと検証結果を提示する。公開依頼に従いレビュー後mainへ反映し、Pagesの完了と匿名HTTPSのmanifest／版を確認する。

静的ホスティングへ配備するZIPは `python tools/package_site.py --output /absolute/path/claudia-help-rev13.zip` で作る。manifestの公開ファイルだけを収録する。ZIPの中身（index.htmlとv0.7等）を指定されたdocument rootへ置く。配置先が判明するまでは既存ファイルを削除・上書きしない。

## 生成元からの移行

旧版の生成元はインフラ文書専用枝の `docs/public-site` / `tools/public-docs.py`、固定commit `a74d5a77afbfbb41d8aeb557c0e547ced46c9ed7`。そのMarkdownは改訂10の公開配布版から引き継いだ。`tools/contract_renderer.py` は同commitの公開レンダリング関数を再利用したもの。インフラ・BFF・MCPの実装／設定は変更しない。

本改訂以降、**サイト編集元はこの公開repoに置く**。旧生成器のstageはHTMLとREADMEを上書きするため、使用しない。インフラ契約を更新するときは、レビュー済みの固定版から公開加工済み `openapi.json` / `api-inventory.json` / `mcp-tools.json` / 合成例を明示取り込みし、`site-source/site.json` のAPI版・対象日・公開ファイルSHAを更新して本生成器を実行する。HTMLは毎回全体を再生成するため、手編集は不要。サイト用ソースと生成物を同じPRで更新する。

## バージョンと対象範囲

文書対象は API 0.7.0-experimental、2026-10-07固定契約スナップショット。実サービスの現在版・配備commit・実機疎通は保証しない。API／MCP／画像の状態は版付きの案内として記載する。新しい版は新ディレクトリを追加して旧版を残す。`manifest.json` はサイト公開対象のSHAを収録し、編集用スクリプトを対象に含めない。

## カスタムドメイン

claudia-help.meta-xdesign.com は確認時、別サーバーのAレコードを指していた。ユーザー設定済みの向き先を保持する。現在のサーバーへ既存の配備方法でファイルを配置する。GitHub PagesへのDNS付け替えを勝手に行わない。新credential発行、Cloudflareへの永続アクセス追加、セキュリティ変更はこのサイト公開に含めない。設定後はDNSの向き先、HTTPS証明書、実URL、canonical／sitemap／linksとmanifest SHAの一致を確認する。

## 契約・語句の照合

改訂12は固定元契約commit `74b35558b25da7c8d7bbb0be18f74b79e8765316` を取り込み、134操作・3追加型を公開加工した。元契約SHA、公開契約SHA、目録、manifest、文書日・改訂は同時に更新する。来歴は `v0.7/provenance.json` に記録する。ブランチ先頭を稼働版として引用しない。

MCP定義は確認した配布ZIPのクライアントから抽出し、1.0.1・8ツール・入力・annotationsを照合済み。client source、ZIP、CAのSHAを来歴に残す。1.0.1表記だけで別ビルドの同一性を保証しない。公開読取の報告はIssue 16に基づき、文書改訂での再実行ではない。

`verify_site.py` は個人・役割メールの未確認掲載、旧業務語、特定の画像例、根拠のない企業セキュリティ表現を検出する。メールは実提供が確認されるまで追加しない。公開受付は既存Issuesを使い、実接続先・資格・顧客情報は非公開で交付する。Dropbox限定認証条件の実装者確認を独立受入や全環境保証へ拡張しない。

## GitHubでの先行共有

改訂13はREADMEから版付きMarkdown・仕様・接続依頼・開発移行手順・公開Issuesへ案内する。ガイドの相互リンクはGitHub上でも同じ文書版へ留まり、HTML生成時に表示用の相対リンクへ変換する。`python tools/verify_github_entry.py` で入口・相対導線・移行要件と準備中状態・公開Issue手順を確認する。

顧客へリポジトリの入口を案内する前に、最新mainへの反映、提供状態、申請・開発経路、公開情報の安全、Issue受付を確認する。改訂13作業の指示はdraft PR更新・pushまでで、mainマージや顧客への送信は行わない。静的サイト配備はGitHubでの先行共有の必須条件ではない。

Mac→VPSの同一クライアント・2 URI併存・設定による移行は設計要件。確認した登録回答は既存public clientの方式で、アプリごとの登録・併存仕様の正本にはならない。ループバックscheme/portとCookie、公開CA入口の交付、URI削除と資格失効の独立受入は確認待ちとして残す。顧客端末へSSH転送・独自CA登録を要求する代替手順は作らない。
