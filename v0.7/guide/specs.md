# 仕様ファイル

機械で読める仕様を、次のファイルで配信しています。ツールの連携や、AIが参照するときに使います。

## ファイル

- [OpenAPI 3.1 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/openapi.json)：134操作の、入力・応答・認証の定義。
- [全API一覧 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/api-inventory.json)：公開する134操作の一覧と、それぞれの提供状態。
- [現在のMCPツール定義 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp-tools.json)：取込アダプターの8ツール。
- [このガイドのMarkdown](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/index.md)：AIやテキストのツールが参照するための形式。
- [実行例のJSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/public-requests.json)：[HTTP・実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/examples.md)の元のデータ。

OpenAPIの接続先と認証のURLは、接続できない説明用の値です。環境に合わせた版の作り方は、[利用者として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/authentication.md)の「OpenAPIのツールから使う」を参照してください。

## 固定した契約と確認記録

契約は2026-10-07のAPI 0.7.0-experimental、文書改訂12です。[来歴JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/provenance.json)に元契約の固定commit・SHA、MCP配布物の版・SHA、確認範囲を記録しています。私有repoへのリンクやローカルの経路を利用者の導線には使いません。

## ファイルの整合を確認する

[manifest](https://mxd2024.github.io/claudia-partner-docs/manifest.json)に、公開しているファイルのSHA-256を記載しています。取得したファイルは、manifestの`files`の値と照合できます。

- `files["v0.7/openapi.json"]`は、公開用に題名や説明を整えた、配信ファイルそのもののSHA-256です。ダウンロードしたOpenAPIは、この値と照合します。
- `source_openapi_sha256`は、公開用に整える前の、元のOpenAPIの値です。配信ファイルとは、一致しません。
- manifest自身は、自己参照を避けるため、`files`に含みません。
- MCPクライアントのZIPのSHA-256は、manifestには含みません。[MCPの導入](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/mcp.md)に載せています。

照合のコマンドは、Windowsは`Get-FileHash -Algorithm SHA256`、macOSは`shasum -a 256`、Linuxは`sha256sum`です。

## アプリからこのドキュメントへリンクする

アプリからリンクするときは、利用しているAPIの版に対応した、`/v0.7/`のURLを使います。[アプリ向けのリンク定義](https://mxd2024.github.io/claudia-partner-docs/links.json)に、安定したリンク先を記載しています。
