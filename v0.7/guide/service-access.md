# service として接続する

serviceは、人の操作なしに動く処理（バッチや連携など）が、基盤に接続するための方式です。利用者がログインする方式（[利用者として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/authentication.md)）とは、別の方式です。

serviceは、組織の管理者の承認を受けて、動きます。承認された、表、列、操作、期限の範囲だけで動き、それを超えることはできません。

## 登場するもの

- **あなたのサーバー処理**: serviceとして動く処理です。登録した鍵を持ちます。
- **組織の管理者**: serviceを申請の内容どおりに承認し、使える状態にします。
- **認証サービス**: 署名された要求を確認して、serviceにトークンを発行します。
- **基盤**: トークンを確認し、承認された範囲で、APIを実行します。

## 全体の流れ

1. あなたが、serviceの利用を申請します（公開鍵を添えます）。
2. 組織の管理者が、申請を承認し、使える状態（provision）にします。
3. あなたのサーバー処理が、秘密鍵で署名した要求を、認証サービスに送り、トークンを受け取ります。
4. 初めて使うときに、有効化（activate）を行います。
5. トークンを付けて、許可された操作を呼びます。

## 前提

- 環境管理者から、接続情報を受け取っていること。
- 組織の管理者が、MFA付きの利用者の資格で、service-clientsを操作できること。
- 秘密鍵は、あなたのサーバー処理だけが持ちます。申請には、公開鍵（JWK）だけを渡します。RSA 2048〜4096ビット、RS256、`kid`付きの鍵を使います。秘密鍵を、API、MCP、チャットへ送らないでください。

## 申請から利用まで

1. **申請する（組織の管理者。申請の内容は、あなたが決めて、管理者に渡します）。** `POST /v2/service-clients`に、`Idempotency-Key`（UUID）を付けて、`app_id`、`purpose`、`expires_at`、`rpm`、`jwk`、`scopes`を送ります。期限は最大90日、`rpm`（1分あたりの要求の上限）は1〜120です。`scopes`には、表、`schema_version`、読む列、書く列、操作、行を明示します。`create`を許可するときは、`custodian`も設定します。
2. **承認する（組織の管理者）。** 返ったclient idと`version`を使い、`POST /v2/service-clients/{clientId}/approve`に`{"version":現在の版}`を送ります。
3. **provisionする（組織の管理者）。** 最新の`version`で、`/provision`を実行します。`ready`の状態と、接続の情報（issuer、`token_endpoint`、audience、`auth_method`）を取得します。
4. **トークンを取得する（あなたのサーバー処理）。** 次のJWT（署名付きの要求）を、登録した鍵で署名し、`token_endpoint`へ送ります。JWTの本体は、記録も表示もしません。`iss`と`sub`、およびフォームの`client_id`には、応答の`client_id`（文字列）を使います。2〜3の、パスの`{clientId}`には、応答の`id`（UUID）を使います。2つは別の値です。`iss`と`sub`、およびフォームの`client_id`には、応答の`client_id`（文字列）を使います。2〜3の、パスの`{clientId}`には、応答の`id`（UUID）を使います。2つは別の値です。

```json
{"iss":"<CLIENT_ID>","sub":"<CLIENT_ID>","aud":"<TOKEN_ENDPOINT>","iat":<現在のUnix秒>,"exp":<現在のUnix秒+30>,"jti":"<一回限りのUUID>"}
```

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=client_credentials&client_id=<CLIENT_ID>&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion=<SIGNED_JWT>
```

5. **activateする（あなたのサーバー処理）。** `access_token`で、`POST /v2/service/activate`に`{}`を送ります。serviceの`access_token`の有効期間は、最大300秒です。更新は、新しい`jti`で、`client_credentials`を取得し直します。利用者用のリフレッシュトークンは、使いません。
6. **使う（あなたのサーバー処理）。** 許可された`POST /v2/service/tables/{collection}/query`を実行します。

**期待する結果**: 許可された操作が、200で成功します。`GET /v1/me`は、人の利用者の専用なので、拒否されます。環境の認証の入口によって、401（`TOKEN_INVALID`）または403のどちらかになります。実際のHTTPとcodeを記録してください。「人として接続できた」ことを、成功の条件にしないでください。

## 権限の変更

serviceの権限（表、列、操作）は、`PUT /v2/service-clients/{clientId}/permissions`で、**全置換**で更新します。省略した表、列、操作は、許可から外れます。有効なserviceは、同じJWTのままで、次の要求から、新しい設定に従います。通常の設定変更で、provisionやactivateを、やり直す必要はありません。

## 権限の変更

serviceの権限（表、列、操作）は、`PUT /v2/service-clients/{clientId}/permissions`で、**全置換**で更新します。省略した表、列、操作は、許可から外れます。有効なserviceは、同じJWTのままで、次の要求から、新しい設定に従います。通常の設定変更で、provisionやactivateを、やり直す必要はありません。

## 停止と失効

suspend（一時停止）またはrevoke（失効）の後は、古いJWTが拒否されることを確認します。resume（再開）の後も、古いJWTを再利用しません。状態に応じて、provision、新しいトークンの取得、activateを行います。変更のAPIは、最新の`version`を要求します。

## 次に

許可された範囲での読み書きは、[表とデータの更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/tables.md)。通しの手順は、[アプリの登録と運用](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/tutorial.md)。
