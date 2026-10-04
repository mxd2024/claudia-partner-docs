# Claudia Partner Docs

API・MCPの共通公開ドキュメントです。

https://mxd2024.github.io/claudia-partner-docs/

このリポジトリは選択した公開資料の生成済み配布物です。API接続先・顧客情報・資格は含みません。manifest.jsonで各ファイルのSHA-256を確認できます。source_openapi_sha256は加工前の元OpenAPI、filesの値は公開処理後の配信ファイルのSHA-256です。取得したopenapi.jsonの完全性はfilesのv0.7/openapi.jsonと照合します。manifest自体は自己参照を避けてfilesに含めません。修正はインフラ側のドキュメント正本で行い、検査した配布物を更新します。
