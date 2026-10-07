# Claudia Partner 開発者ヘルプ

ガイド・API・リリース情報をまとめた公開静的サイトです。

公開先（指定）: https://claudia-help.meta-xdesign.com/
既存GitHub Pages: https://mxd2024.github.io/claudia-partner-docs/

文書対象はAPI **0.7.0-experimental / 2026-10-04契約**、文書改訂11。現在稼働するAPIの版・配備状態・実機疎通を保証しません。接続先、顧客情報、資格は公開対象に含めません。

## 編集と再生成

編集元は `v0.7/guide/*.md`、`site-source/` と公開契約JSONです。Python標準ライブラリで生成できます。

```sh
python tools/build_site.py
python tools/verify_site.py
python -m http.server 8765 --bind 127.0.0.1
```

生成HTMLを直接編集せず、リポジトリ内の保守手順 `site-source/MAINTAINER.md` から更新してください。旧インフラ生成器による配信先の丸ごと上書きは使用しません。

## 公開ファイルの整合

`manifest.json` の `files` が公開対象の許可リストとSHA-256です。配備用ZIPはこのリストとmanifestだけを収録し、Git・編集スクリプト・個別資料は収録しません。公開OpenAPIは `files["v0.7/openapi.json"]` と照合します。`source_openapi_sha256` は公開加工前の値です。

## 問い合わせ

誤記はこのリポジトリのIssuesへ。接続の相談はサイトの「サポートと窓口」を参照してください。顧客の接続先・資格・実データはIssueへ書かないでください。
