# 画像・添付と外部ストア

業務行のasset_ref欄に、管理された原本、または外部の原本への参照を関連付けます。デザイン画像を表示するアプリも、この共通のメディアAPIを使います。

業務表（v2）の行の画像欄には、`/v2/media`を使います。`/v1/assets`は、親の資源を`namespace`と`resourceType`で指定する、資産の経路です（[APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/openapi.json)の「資産」）。

> 以下の状態は2026-10-04の文書対象版の記録です。今回、実環境での画像動作や正式SSOを再確認していません。画像の機能は、環境ごとの有効化が必要です [環境による]。正式なログイン（SSO・MFA）の環境での、画像の利用は [準備中]、Dropboxのフォルダー選択APIは [未提供] です。この説明だけで、ご利用の環境にDropboxが接続済みという意味にはなりません。

## 管理原本と外部参照

| 保存方式 | 用途 | 解除した場合 |
| --- | --- | --- |
| managed_original | アプリが送った原本を、基盤が保持 | メディアの状態・保持方針に従う |
| external_reference | Dropbox等の原本を複製せず、業務行へ関連付ける | 関連の解除。外部原本は削除しない |

外部原本の配置・整理・バックアップは原本の管理者が担当します。サムネイルや一時取得ファイルは、原本のバックアップにはなりません。

## 参照を登録して表示する

1. asset_ref欄を持つ表定義と業務行を用意します。
2. 次のpolicyを取得し、現在の許可、媒体、上限、reference_stores、必要な版を確認します。
3. 新しい画像には、`assetId`として、新しいUUIDを、呼び出し側で作ります。policyが返すstoreと、その中の相対パスを使い、参照を登録します。
4. 添付一覧・metadataを取得し、認可された経路からthumbnailまたはcontentを表示します。

```http
GET /v2/media/{collection}/{rowId}/{field}/policy
GET /v2/media/{collection}/{rowId}/{field}
POST /v2/media/{collection}/{rowId}/{field}/{assetId}/reference
GET /v2/media/{collection}/{rowId}/{field}/{assetId}/thumbnail
GET /v2/media/{collection}/{rowId}/{field}/{assetId}/content
```

[完全なヘッダー・要求・応答例](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/examples.md)も参照してください。以下は参照登録の本文だけの例です。storeはpolicyにある値を使い、相対パスは対象ストア内に限定します。次のヘッダーを付けます。`If-Match`は、新しい画像では`"0"`、既存の画像の更新では、取得した画像の現在の版です。`X-Parent-Version`と`X-Schema-Version`は、policyや行の取得で得た、現在の値です。適当な値を作らないでください。`Idempotency-Key`は、操作ごとに、新しく作ります。

```json
{
  "store": "design-images",
  "relative_path": "examples/design-blue.png",
  "media_type": "image/png",
  "name": "デザイン見本"
}
```

APIには、Dropboxの共有URLやOSの絶対パスではなく、policyの`store`と、その中の相対パスを渡します。ブラウザー表示では、あなたのアプリのサーバー側が、画像のバイナリーを取得して、ブラウザーに渡します。AuthorizationをURLへ付けないでください。

参照を登録すると、画像の関連付けと、画像の版が更新されます。親の行の`asset_ref`の値や、親の行の版は、自動では更新されません。親の行に、`assetId`を書き込む操作は不要で、任意のIDやURLの書き込みは、受理されません。画像の表示には、画像の一覧と取得のAPIを使います。関連の解除は、Dropbox上の原本の削除ではありません。

## 外部ストアとDropboxの対応

外部ストアは利用する機能と契約に応じて選びます。Dropboxはすべてのアプリの必須条件ではありません。ここからは、この版で記録されたDropbox参照の例です。

`store`は、環境ごとに、提供者が設定します。policyが、その環境で使える`store`の名前を返します。Dropboxのアカウントと、対象のフォルダーが、どの`store`に対応するかは、提供者が環境ごとに登録して、お客様に渡します。アプリが、パスを指定して、接続を作る仕組みではありません。Dropboxのフォルダーの一覧の取得や、共有URLの変換のAPIは、ありません。

Dropboxの接続は、提供者への初期設定の依頼になります。依頼には、契約と環境、対象のアプリ・表・列、対象のフォルダー、読み取りと保存の用途、原本の保管の責任を、書いてください。[接続情報を依頼する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/request-access.md)の雛形に、欄があります。接続の手順と窓口は、個別に案内します。お客様が自分で接続できる、という意味ではありません。OAuthの秘密などは、メールやチャットに書かないでください。

## 原本の変更・移動・切断

登録時の原本と現在の内容を検査します。変更・移動を勝手に別の原本として採用せず、差分確認と版付きの再関連を行います。外部の原本に到達できないときは、エラーが返ります。空の一覧を、正常な結果として扱わないでください。

業務行の添付一覧は取得できますが、任意のDropboxフォルダーから画像を選ぶ公開一覧や、共有URLを安全に解決する機能は未提供です。アプリは接続・未接続・原本変更を区別して表示します。

## 媒体と上限

- PNG・JPEG・WebPは実形式をデコードして検証します。最大16M画素、サムネイルは320px以内のPNGです。
- 1ファイル最大32MiB、同時処理は2要求、1行1欄に最大100資産です。解除済みIDも上限に含まれます。
- SVGは対象外です。PDFはダウンロードのみ。Range、再開upload、動画変換、マルウェア検疫は未提供です。

実際に利用できる媒体・容量はpolicyを優先してください。認証切れ、権限不足、版競合、媒体不適合、依存停止の扱いは[エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/errors.md)にまとめています。
