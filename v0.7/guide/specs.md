# 仕様ファイル

機械で読める仕様を、次のファイルで配信しています。ツールの連携や、AIが参照するときに使います。

## ファイル

- [OpenAPI 3.1 JSON](../openapi.json)：134操作の、入力・応答・認証の定義。
- [全API一覧 JSON](../api-inventory.json)：公開する134操作の一覧と、それぞれの提供状態。
- [現在のMCPツール定義 JSON](../mcp-tools.json)：取込アダプターの8ツール。
- [このガイドのMarkdown](../guide/index.md)：AIやテキストのツールが参照するための形式。
- [実行例のJSON](../examples/public-requests.json)：[HTTP・実行例](examples.md)の元のデータ。

OpenAPIの接続先と認証のURLは、接続できない説明用の値です。環境に合わせた版の作り方は、[利用者として接続する](authentication.md)の「OpenAPIのツールから使う」を参照してください。

文書改訂11の元OpenAPIは、2026-10-07の固定commit `74b35558b25da7c8d7bbb0be18f74b79e8765316`です。元仕様のSHA-256は`29e0a6fcd763b3efb855ef40dd3018f06cae790a64db3b2e37c26273d333a63b`です。[文書対象の出典情報](../provenance.json)に、対象版とMCP配布物の固定値を記載しています。稼働版は接続先ごとに確認してください。

## ファイルの整合を確認する

[manifest](../../manifest.json)に、公開しているファイルのSHA-256を記載しています。取得したファイルは、manifestの`files`の値と照合できます。

- `files["v0.7/openapi.json"]`は、公開用に題名や説明を整えた、配信ファイルそのもののSHA-256です。ダウンロードしたOpenAPIは、この値と照合します。
- `source_openapi_sha256`は、公開用に整える前の、元のOpenAPIの値です。配信ファイルとは、一致しません。
- manifest自身は、自己参照を避けるため、`files`に含みません。
- MCPクライアントのZIPのSHA-256は、manifestには含みません。[MCPの導入](mcp.md)に載せています。

照合のコマンドは、Windowsは`Get-FileHash -Algorithm SHA256`、macOSは`shasum -a 256`、Linuxは`sha256sum`です。

## アプリからこのドキュメントへリンクする

アプリからリンクするときは、利用しているAPIの版に対応した、`/v0.7/`のURLを使います。[アプリ向けのリンク定義](../../links.json)に、安定したリンク先を記載しています。
