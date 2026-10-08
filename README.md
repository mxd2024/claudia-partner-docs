# Claudia Partner 開発者ドキュメント

顧客アプリ開発者向けの公開ガイド・API仕様です。**GitHub上のMarkdownと仕様ファイルから読み始められます。** 文書の質問・不足する説明は[公開GitHub Issues](https://github.com/mxd2024/claudia-partner-docs/issues)へ。

対象: **API 0.7.0-experimental / 2026-10-07固定契約 / 文書改訂13 / 134操作 / 取込MCP 1.0.1・8ツール**。ブランチ先頭や文書更新日をAPIの稼働版とみなしません。利用環境の版・有効な機能・現在の権限を環境管理者へ確認します。

## 読み始める

| 目的 | ガイド |
| --- | --- |
| 顧客BFF・Core API・認証サービスの全体像 | [アプリ開発の全体像](v0.7/guide/index.md) |
| 提供中・環境による・準備中・未提供の区別 | [対応状況とバージョン](v0.7/guide/versions.md) |
| 接続情報・クライアント登録を相談する | [申請項目と公開Issueの雛形](v0.7/guide/request-access.md) |
| Macで開発してVPS等へ移す設計 | [BFF構成・設定差分・確認手順](v0.7/guide/app-architecture.md) |
| 最初のログインと読取 | [接続準備](v0.7/guide/quickstart.md)・[人のOIDC接続](v0.7/guide/authentication.md) |
| service・取込MCPを使う | [service接続](v0.7/guide/service-access.md)・[取込MCP](v0.7/guide/mcp.md) |
| 機能ごとの実装 | [表と行](v0.7/guide/tables.md)・[メディア](v0.7/guide/media.md)・[競合と再送](v0.7/guide/reliability.md) |
| 例から読む | [架空の業務メモアプリ](v0.7/guide/sample-app.md)・[HTTPの合成例](v0.7/guide/examples.md) |
| 質問・修正を依頼する | [問い合わせ手順](v0.7/guide/support.md)・[既存Issue一覧](https://github.com/mxd2024/claudia-partner-docs/issues) |
| 変更を確認する | [変更履歴](v0.7/guide/changelog.md)・[仕様と整合確認](v0.7/guide/specs.md) |

## API・AIが読む仕様

- [OpenAPI JSON（134操作）](v0.7/openapi.json)、[操作一覧](v0.7/api-inventory.json)。
- [取込MCP定義（1.0.1・8ツール）](v0.7/mcp-tools.json)。全APIのMCPは準備中です。
- [60件の合成要求・応答](v0.7/examples/public-requests.json)。56/134操作をカバーします。実機実行例ではなく、残る例の拡充・実行確認は準備中です。
- [固定出典と確認範囲](v0.7/provenance.json)、[公開ファイルのSHA-256](manifest.json)。

接続先のexample.invalidは架空です。アプリ用クライアント登録・開発／本番の戻り先併存・Mac→VPSの設定移行は準備中で、自己登録は未提供です。ループバックの可否は環境によります。設計手順の掲載を、現在接続可能な経路の保証としません。

## 公開Issueで相談する

既存の同じ話題を検索し、追加質問は該当Issueへ、新しい話題は新規Issueへ。版・ページ・一般化した質問と再現手順を記載します。**顧客名・個人情報・実環境URL・資格・秘密・顧客データ・原票は投稿しません。** 実値は環境管理者の非公開方法で交付します。回答期限・24時間対応を保証していません。

## 静的画面と保守

ホーム・検索・機能別APIのHTMLも生成しています。静的サイトの指定公開先はclaudia-help.meta-xdesign.comですが、まだ配備していません。GitHubでの文書利用に静的配備は必須ではありません。HTMLのブラウザー表示は公開後に案内します。

編集元は`v0.7/guide/*.md`、`site-source/`と公開契約JSON。Python標準ライブラリで再生成できます。生成HTMLを手編集せず、リポジトリ内の`site-source/MAINTAINER.md`を参照してください。

```sh
python tools/build_site.py
python tools/verify_site.py
```

公開資料の掲載だけで、利用環境への接続・権限・準備中機能の提供が完了するわけではありません。対象版・提供条件と環境管理者から交付された情報を照合してください。
