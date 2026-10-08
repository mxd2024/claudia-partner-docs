# Claudia Partner Docs

Claudia Partnerの顧客アプリ開発者向け公開ドキュメントです。

https://mxd2024.github.io/claudia-partner-docs/

API 0.7.0-experimental、文書改訂12（2026-10-08）、固定契約2026-10-07を対象にします。文書の最新版は接続先の稼働版を意味しません。134操作、MCPクライアント1.0.1の8ツールを記載し、有効化・権限・実機確認範囲は利用環境ごとに区別します。

## 更新とビルド

`content-source/pages/`を編集し、`python tools/build_content.py`で配信用HTML、Markdown、検索索引、manifestを生成します。`tools/public_renderer.py`は元サイトの描画処理です。スタイル・JavaScript・ロゴ・図の座標を更新する処理はありません。機械仕様は既存の`v0.7/*.json`、出典は`v0.7/provenance.json`、対象版は`content-source/site.json`にあります。`python tools/build_content.py --check`と`python tools/verify_content.py`で生成結果・リンク・仕様・元の視覚構造を確認できます。

GitHub Pagesはmainのルートを公開します。文書更新はPRでレビューし、main反映後にPagesの完了と公開URLを確認します。新しいVPS・Docker・API実行機能・認証画面は設けません。

## ファイルの整合

manifest.jsonの`files`に配信ファイルのSHA-256を記載します。`source_openapi_sha256`は公開用加工前の固定仕様の値です。公開用OpenAPIとは値が異なります。`v0.7/provenance.json`に対象版の出典と確認範囲を記載します。

## 誤記・質問

[公開Issues](https://github.com/mxd2024/claudia-partner-docs/issues)へお寄せください。顧客の名前・実データ・実際の接続先・資格は投稿しないでください。非公開情報が必要な相談は、利用環境で定められた連絡方法に従います。
