# 利用者として接続する

「利用者として接続する」とは、利用者が認証サービスでログインし、顧客アプリが、その利用者の資格（アクセストークン）を受け取って、基盤APIを呼ぶことです。基盤は、その利用者の権限の範囲で、操作を許可します。

このページでは、登録済みclient_idとredirect_uriを受け取れる利用環境で、ログインから最初の`GET /v1/me`が200になるまでを説明します。個別アプリのクライアント登録・BFF接続は準備中、自己登録UI/APIは未提供です。MCPの接続キーは、この方式とは別の資格です。

顧客アプリ・基盤API・認証サービスの違いは、[用語集](glossary.md)を参照してください。

## 登場するもの

- **利用者**: ログインする人です。
- **顧客アプリ**: 利用者に代わって、基盤APIを呼びます。
- **認証サービス**: 利用者を確認し、ログインを完了させます。
- **基盤**: アクセストークンを確認し、利用者の権限で、APIを実行します。

## 全体の流れ

1. 顧客アプリが、利用者を、認証サービスのログイン画面へ案内します。
2. 利用者が、ログインし、MFA（パスワードに加えるもう1つの確認）を完了します。
3. 認証サービスが、利用者を顧客アプリへ戻し、一時的な「認可コード」を渡します。
4. 顧客アプリが、認可コードを、アクセストークンに交換します。
5. 顧客アプリが、アクセストークンを付けて、基盤APIを呼びます。

この方式は、OIDC（OpenID Connect。ログインの標準の方式）の、Authorization Code + PKCEです。PKCEは、認可コードを盗まれても使えないようにする仕組みです。

## ログインして、トークンを取得する

1. 環境管理者から、issuer（認証サービスのURL）、client_id（アプリのID）、登録済みのredirect_uri（ログイン後に戻るURL）、scope（求める権限の種類）、基盤のHTTPS originを受け取ります。client_idは、自分で決めません。検証用のredirect_uriが必要なら、利用環境で登録可能な値を確認します。loopbackの利用可否は利用環境によります。
2. issuerの`/.well-known/openid-configuration`をHTTPSで読み、返るissuerが、受け取った値と一致することを確認します。`authorization_endpoint`と`token_endpoint`を控えます。
3. 暗号学的な乱数で、`state`と`code_verifier`を作ります。`code_verifier`は、43〜128文字の、URLに安全な文字列です。`code_challenge`は、`code_verifier`のSHA-256を、base64urlにした値（末尾の`=`なし）です。`code_verifier`と`state`は、ログに出さず、1回のログインにだけ使います。
4. 次の認可URLを、ブラウザーで開き、利用者にログインとMFAを完了してもらいます。パラメーターは、URLエンコードします。

```http
GET <authorization_endpoint>?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&scope=<受け取ったscope>&state=<RANDOM_STATE>&code_challenge=<S256_CHALLENGE>&code_challenge_method=S256
```

5. 戻り先（redirect_uri）で受け取った`state`を、保持した値と照合します。一致しない場合や、エラーの場合は、中断します。受け取った`code`を、1回だけ、トークンに交換します。

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=authorization_code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&code=<CODE>&code_verifier=<VERIFIER>
```

クライアントは、トークンの交換でクライアントシークレットを使わない、公開クライアント（public client）です。PKCEを使います。`scope`は、利用環境で渡された値（通常は`openid`）です。アクセストークンに必要な、追加の値は、認証サービスの設定が付けます。トークンを自作して、補うことはできません。`offline_access`を、一般の必須のscopeとして、追加しないでください。

応答の`access_token`、`token_type`、`expires_in`を使います。リフレッシュトークンが発行されるかは、クライアントの設定によります。IDトークンは、利用者の情報を知るためのもので、基盤APIの呼び出しには使いません。

## 最初のAPI呼び出し

取得した`access_token`を使い、`GET /v1/me`を呼びます。`GET /v1/me`は、いま、誰として接続しているかを返すAPIです。

```sh
curl -sS -H "Authorization: Bearer $CP_ACCESS_TOKEN" -H "Accept: application/json" https://<基盤のHTTPS origin>/v1/me
```

ヘッダー込みの完全な例は、[HTTP・実行例](examples.md)の「利用者を確認」にあります。TLSの検証は、無効にしません。

**期待する結果**: 200が返り、利用者のid、permissions（権限）、capabilities、セッションの期限が含まれます。permissionsが空でも、確認は成功です。表の操作が許可されている、という意味ではありません。

| 結果 | 確認すること |
| --- | --- |
| 401 | issuer、audience、client、期限、セッション |
| 403 | 現在の権限と、MFA |

署名の検査や認可を無効にして、接続を通さないでください。

### ログイン直後の反映待ち

ログインした直後は、数秒から十数秒の間、`GET /v1/me`が401（`TOKEN_INVALID`）になることがあります。待ち時間の上限は、保証しません。

- ログイン直後の`GET /v1/me`に限って、回数と時間を決めて、待ってから再確認します。待機の枠の例は、0.5秒間隔で、最大20秒です。
- 20秒を過ぎても成功しないときは、待つのをやめ、時刻、code、`request_id`を控えて、環境管理者に確認します。
- `TOKEN_EXPIRED`、明示的な失効、403、TLSや署名のエラーでは、待ちません。変更の操作は、自動で再送しません。

## MFAと再認証

MFAが必要な操作では、アクセストークンが、MFAを完了した認証であること（`acr`）を、確認します。再認証が必要な操作は、最後に認証した時刻（`auth_time`）と、操作ごとの最大の経過時間で、判断されます。

403で`MFA_REQUIRED`または`REAUTH_REQUIRED`が返ったときは、ログインの手順（認可コードフロー）を、最初から、やり直し、MFAを完了します。トークンの更新（リフレッシュ）では、代用できません。認可のURLに、`max_age`や`prompt=login`などを付けるだけでは、受理が保証されません。MFAと再認証の設定は、利用環境ごとの認証サービスで行います。具体的な手順は、環境管理者に確認してください。

## トークンの更新と、ログアウト

アクセストークンには、有効期限があります。リフレッシュトークンを発行されたクライアントは、期限が切れる前に、トークンを更新できます。

- `token_endpoint`に、`grant_type=refresh_token`、`client_id`、`refresh_token`を、フォームで送ります。
- 新しいリフレッシュトークンが返ったときは、安全に保存してから、次の利用へ進みます。
- 同じ利用者のセッションの更新は、1つずつ行います。古いトークンを、再利用しません。
- `invalid_grant`が返ったときは、更新を繰り返さず、再ログインへ戻ります。

ログアウトは、`POST /v2/session/logout`で行います（利用者用）。

```json
{"attempt_id":"<UUID>"}
```

成功すると、`{"status":"revoked","attempt_id":"<同じUUID>","request_id":"<UUID>"}`が返ります。結果が不明なときは、同じ`attempt_id`で再送します。このルートでは、`Idempotency-Key`ヘッダーは要りません。

## OpenAPIのツールから使う

公開のOpenAPIの接続先と認証のURLは、接続できない説明用の`example.invalid`です。公開ファイルに、実際の接続情報を書き込まず、[利用環境版の生成ツール](../examples/configure-openapi.py)と[接続情報の雛形](../examples/environment.example.json)で、手元に利用環境版を作ります。

```sh
python configure-openapi.py --source openapi.json --profile environment.json --output openapi.environment.json
```

生成したファイルを、対応するツールに読み込み、PKCEに対応したOIDC認証と、登録済みのclient_id・redirect_uriを設定します。利用環境版には、接続情報が含まれます。公開のリポジトリには、置かないでください。

## 権限について

管理権限（`manage_access`と`service_administrator`）と、表の読み取り・書き込み・設計の権限は、別です。表、列、行、期限は、操作のたびに確認されます。利用者を助けるAIも、利用者の権限を超えられません。詳しくは、[基盤の考え方と責任分界](principles.md)と、[MCPの導入](mcp.md)。
