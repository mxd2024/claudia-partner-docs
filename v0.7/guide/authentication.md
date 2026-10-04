# 本人として接続する

本人としての接続は、Authorization Code + PKCEで行います。ここでは、ログインから、最初の`GET /v1/me`が200になるまでを示します。MCPの接続キーは、この方式とは別の資格です。

## ログインして、トークンを取得する

1. 環境管理者から、issuer、client_id、登録済みのredirect_uri、scope、基盤のHTTPS originを受け取ります。client_idは、自分で決めません。アプリをまだ作っていないときの検証用のredirect_uriが必要なら、依頼の雛形の「redirect_uri」欄に、希望を書いてください。
2. issuerの`/.well-known/openid-configuration`をHTTPSで読み、返るissuerが、受け取った値と一致することを確認します。`authorization_endpoint`と`token_endpoint`を控えます。
3. 暗号学的な乱数で、`state`と`code_verifier`を作ります。verifierは、43〜128文字のURLに安全な文字列です。`code_challenge`は、SHA-256(verifier)のbase64url（末尾の=なし）です。verifierとstateは、ログに出さず、1回の試行にだけ使います。
4. 次の認可URLを、ブラウザーで開き、ログインとMFAを完了します。パラメーターは、URLエンコードします。

```http
GET <authorization_endpoint>?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&scope=<受け取ったscope>&state=<RANDOM_STATE>&code_challenge=<S256_CHALLENGE>&code_challenge_method=S256
```

5. 戻り先（redirect_uri）の`state`を、保持した値と照合します。一致しない場合や、エラーの場合は、中断します。受け取った`code`を、1回だけ交換します。

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=authorization_code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&code=<CODE>&code_verifier=<VERIFIER>
```

応答の`access_token`、`token_type`、`expires_in`を使います。リフレッシュトークンが発行されるかは、クライアントの設定によります。IDトークンは、本人の情報のためのもので、基盤APIの呼び出しには使いません。

## 最初のAPI呼び出し

取得した`access_token`を使い、`GET /v1/me`を呼びます。

```sh
curl -sS -H "Authorization: Bearer $CP_ACCESS_TOKEN" -H "Accept: application/json" https://<基盤のHTTPS origin>/v1/me
```

ヘッダー込みの完全な例は、[HTTP・実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)の「本人を確認」にあります。TLSの検証は、無効にしません。

**期待する結果**: 200が返り、本人のid、permissions、capabilities、セッションの期限が含まれる。permissionsが空でも、本人確認の成功です。表の操作の許可を意味しません。

| 結果 | 確認すること |
| --- | --- |
| 401 | issuer、audience、client、期限、セッション |
| 403 | 現在の権限と、MFA |

署名の検査や認可を無効にして、接続を通さないでください。

### ログイン直後の反映待ち

新しくログインした直後は、数秒から十数秒の間、`GET /v1/me`が401（`TOKEN_INVALID`）になることがあります。上限は保証しません。

- 正常に完了した、ログイン直後の`GET /v1/me`だけで、回数と時間を限って、待ってから再確認します。待機の枠の例は、0.5秒間隔で、最大20秒です。
- 20秒を過ぎても成功しない場合は、待機を終え、時刻、code、`request_id`を控えて、環境管理者に確認します。
- `TOKEN_EXPIRED`、明示的な失効、403、TLSや署名のエラーでは、待機しません。変更の操作を、自動で再送しません。

## 更新と失効

リフレッシュに対応するクライアントは、`token_endpoint`に、`grant_type=refresh_token`、`client_id`、`refresh_token`を、フォームで送ります。新しいリフレッシュトークンが返ったときは、安全に保存してから、次の利用へ進みます。同じ本人のセッションの更新は、1つずつ行い、古いトークンを再利用しません。`invalid_grant`のときは、更新を繰り返さず、再ログインへ戻ります。

ログアウトは、`POST /v2/session/logout`で行います（本人用）。

```json
{"attempt_id":"<UUID>"}
```

成功の応答は、`{"status":"revoked","attempt_id":"<同じUUID>","request_id":"<UUID>"}`です。結果が不明なときは、同じ`attempt_id`で再送します。このルートでは、`Idempotency-Key`ヘッダーは不要です。

## OpenAPIのツールから使う

公開のOpenAPIの接続先と認証のURLは、接続できない説明用の`example.invalid`です。公開ファイルに、実際の接続情報を書き込まず、[環境版の生成ツール](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/configure-openapi.py)と[接続情報の雛形](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/environment.example.json)で、手元に環境版を作ります。

```sh
python configure-openapi.py --source openapi.json --profile environment.json --output openapi.environment.json
```

生成したファイルを、対応するツールに読み込み、PKCEに対応したOIDC認証と、登録済みのclient_id・redirect_uriを設定します。環境版には、接続情報が含まれるため、公開のリポジトリに置かないでください。

## 権限について

管理者の権限（`can_manage_access`）と、表の読み取り・書き込み・設計の権限は、別です。表・列・行・期限は、操作のたびに確認されます。本人を支援するAIも、本人の権限を超えられません。詳しくは、[基盤の考え方と責任分界](https://mxd2024.github.io/claudia-partner-docs/v0.7/principles.html)と、[MCPの導入](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html)。
