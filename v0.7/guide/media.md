# 画像とDropbox連携

業務行のasset_ref欄に、管理された原本、または外部の原本への参照を関連付けます。デザイン画像を表示するアプリも、この共通のメディアAPIを使います。

業務表（v2）の行の画像欄には、`/v2/media`を使います。`/v1/assets`は、親の資源を`namespace`と`resourceType`で指定する、資産の経路です（[APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/openapi.json)の「資産」）。

> 画像の機能は、環境ごとの有効化が必要です [環境による]。本人のセッションと組み合わせた画像の利用は [準備中]、Dropboxのフォルダー選択APIは [未提供] です。この説明だけで、ご利用の環境にDropboxが接続済みという意味にはなりません。

## 管理原本と外部参照

| 保存方式 | 用途 | 解除した場合 |
| --- | --- | --- |
| managed_original | アプリが送った原本を、基盤が保持 | メディアの状態・保持方針に従う |
| external_reference | Dropbox等の原本を複製せず、業務行へ関連付ける | 関連の解除。外部原本は削除しない |

外部原本の配置・整理・バックアップは原本の管理者が担当します。サムネイルや一時取得ファイルは、原本のバックアップにはなりません。

## 参照を登録して表示する

1. asset_ref欄を持つ表定義と業務行を用意します。
2. 次のpolicyを取得し、現在の許可、媒体、上限、reference_stores、必要な版を確認します。
3. 許可されたstore IDと安全な相対パスを使い、参照を登録します。
4. 添付一覧・metadataを取得し、認可された経路からthumbnailまたはcontentを表示します。

```http
GET /v2/media/{collection}/{rowId}/{field}/policy
POST /v2/media/{collection}/{rowId}/{field}/{assetId}/reference
GET /v2/media/{collection}/{rowId}/{field}/{assetId}/thumbnail
GET /v2/media/{collection}/{rowId}/{field}/{assetId}/content
```

[完全なヘッダー・要求・応答例](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/examples.md)も参照してください。以下は参照登録の本文だけの例です。storeはpolicyにある値を使い、相対パスは対象ストア内に限定します。リクエストにはAPI仕様に従いIf-Match、Idempotency-Key、X-Parent-Version、X-Schema-Versionを付けます。

```json
{
  "store": "design-images",
  "relative_path": "examples/design-blue.png",
  "media_type": "image/png",
  "name": "デザイン見本"
}
```

APIには、Dropboxの共有URLやOSの絶対パスではなく、policyの`store`と、その中の相対パスを渡します。ブラウザー表示では認可済みクライアントがbinaryを取得し、Blobなどを使います。AuthorizationをURLへ付けないでください。

## 原本の変更・移動・切断

登録時の原本と現在の内容を検査します。変更・移動を勝手に別の原本として採用せず、差分確認と版付きの再関連を行います。外部の原本に到達できないときは、エラーが返ります。空の一覧を、正常な結果として扱わないでください。

業務行の添付一覧は取得できますが、任意のDropboxフォルダーから画像を選ぶ公開一覧や、共有URLを安全に解決する機能は未提供です。アプリは接続・未接続・原本変更を区別して表示します。

## 媒体と上限

- PNG・JPEG・WebPは実形式をデコードして検証します。最大16M画素、サムネイルは320px以内のPNGです。
- 1ファイル最大32MiB、同時処理は2要求、1行1欄に最大100資産です。解除済みIDも上限に含まれます。
- SVGは対象外です。PDFはダウンロードのみ。Range、再開upload、動画変換、マルウェア検疫は未提供です。

実際に利用できる媒体・容量はpolicyを優先してください。認証切れ、権限不足、版競合、媒体不適合、依存停止の扱いは[エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/errors.md)にまとめています。
