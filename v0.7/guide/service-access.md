# service として接続する

serviceは、人の操作を介さない処理（バッチ、連携など）が、基盤に接続するための方式です。管理者の承認を受け、承認された表、列、操作、期限の範囲だけで動きます。

## 前提

- 環境管理者から、接続情報を受け取っていること。
- あなたの組織の管理者が、MFA付きの本人の資格で、service-clientsを操作できること。
- 秘密鍵は、service側だけが持ちます。申請には、公開鍵（JWK）だけを渡します。RSA 2048〜4096ビット、RS256、`kid`付き。秘密鍵を、API、MCP、チャットへ送らないでください。

## 申請から利用まで

1. **申請する（開発者）。** `POST /v2/service-clients`に、`app_id`、`purpose`、`expires_at`、`rpm`、`jwk`、`scopes`を送ります。期限は最大90日、rpmは1〜120です。`scopes`には、表、`schema_version`、読む列、書く列、操作、行を明示します。`create`を許可するときは、`custodian`も設定します。
2. **承認する（あなたの組織の管理者）。** 返ったclient idと`version`を使い、`POST /v2/service-clients/{clientId}/approve`に`{"version":現在の版}`を送ります。
3. **provisionする（あなたの組織の管理者）。** 最新の`version`で、`/provision`を実行します。`ready`の状態と、接続の情報（issuer、`token_endpoint`、audience、`auth_method`）を取得します。
4. **トークンを取得する（あなたのサーバー処理）。** 次のJWTを、登録した鍵で署名し、`token_endpoint`へ送ります。JWTの本体は、記録も表示もしません。

```json
{"iss":"<CLIENT_ID>","sub":"<CLIENT_ID>","aud":"<TOKEN_ENDPOINT>","iat":<現在のUnix秒>,"exp":<現在のUnix秒+30>,"jti":"<一回限りのUUID>"}
```

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=client_credentials&client_id=<CLIENT_ID>&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion=<SIGNED_JWT>
```

5. **activateする。** `access_token`で、`POST /v2/service/activate`に`{}`を送ります。serviceの`access_token`の有効期間は、最大300秒です。更新は、新しい`jti`で、`client_credentials`を取得し直します。本人用のリフレッシュトークンは使いません。
6. **使う。** 許可された`POST /v2/service/tables/{collection}/query`を実行します。

**期待する結果**: 許可された操作が、200で成功する。`GET /v1/me`は人専用なので、拒否される。環境の認証の入口によって、401（`TOKEN_INVALID`）または403のどちらかになるため、実際のHTTPとcodeを記録します。「人として接続できた」ことを、成功の条件にしません。

## 停止・失効

suspendまたはrevokeの後は、古いJWTが拒否されることを確認します。resumeの後も、古いJWTを再利用せず、状態に応じて、provision、新しいトークンの取得、activateを行います。変更のAPIは、最新の`version`を要求します。

## 次に

許可された範囲での読み書きは、[表とデータの更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/tables.html)。通しの手順は、[アプリの登録と運用](https://mxd2024.github.io/claudia-partner-docs/v0.7/tutorial.html)。
