# 認証・権限

本人接続はAuthorization Code + PKCE、service接続は登録されたRSA鍵によるprivate_key_jwtを使います。MCP取込キーは、この2方式とは別の顧客アプリ用資格です。

## 本人: Authorization Code + PKCE

1. 管理者からissuer、client_id、登録済みredirect_uri、scope、Core originを取得します。Coreの本人クライアントは現在hub-spaに制限される経路があります。任意のclient_idを自分で決めないでください。
2. issuerの /.well-known/openid-configuration をHTTPSで読み、返るissuerが交付値と一致すること、authorization_endpointとtoken_endpointを確認します。
3. 暗号学的乱数でstateとcode_verifierを生成します。verifierは43〜128文字のURL安全な文字列、code_challengeはSHA-256(verifier)のbase64url（末尾=なし）です。verifierとstateをログに出さず、一回の試行に束縛します。
4. 次の認可URLをブラウザーで開き、本人ログインとMFAを完了します。パラメーターはURLエンコードします。

```http
GET <authorization_endpoint>?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&scope=openid&state=<RANDOM_STATE>&code_challenge=<S256_CHALLENGE>&code_challenge_method=S256
```

5. callbackのstateを保持値と照合します。不一致・エラーなら中断します。受け取ったcodeを一度だけ交換します。

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=authorization_code&client_id=<CLIENT_ID>&redirect_uri=<REGISTERED_REDIRECT_URI>&code=<CODE>&code_verifier=<VERIFIER>
```

200のaccess_token、token_type、expires_inを扱います。refresh_tokenが発行されるかはクライアント設定に従います。ID tokenは本人情報のためのもので、CoreへのBearerには使いません。提供BFF以外のクライアントは独自にrefreshを約束せず、登録条件を確認してください。

## refresh・失効

refresh対応クライアントはtoken_endpointへ grant_type=refresh_token、client_id、refresh_tokenをform送信します。rotationでは返った新しいrefresh_tokenを安全に永続化してから次の利用へ進みます。同じ本人セッションの更新を直列化し、古いtokenの再利用を避けます。invalid_grantでは更新を繰り返さず再ログインへ戻します。期限はIdP設定と /v1/me の現在セッションを基準にします。

POST /v2/session/logout は本人用です。本文は {"attempt_id":"<UUID>"}、成功は {"status":"revoked","attempt_id":"<同じUUID>","request_id":"<UUID>"}。結果不明時には同じattempt_idを保持します。Idempotency-Keyヘッダーはこの経路の必須条件ではありません。

## service: 申請から利用まで

管理者がMFA付き本人資格でservice-clientsを操作します。サービス側は秘密鍵を保持し、公開JWKのみを申請へ渡します。RSA 2048〜4096bit、RS256、kid付き。秘密鍵をAPI・MCP・チャットへ送らないでください。

1. POST /v2/service-clients: app_id、purpose、expires_at、rpm、jwk、scopesを申請します。期限は最大90日、rpmは1〜120。scopesは表・schema_version・read列・write列・operations・rowsを明示。createを許可するときはcustodianも設定します。
2. 返ったclient idとversionを使い、POST /v2/service-clients/{clientId}/approve に {"version":現在版} を送ります。
3. 最新versionで /provision を実行します。ready状態とconnectionのissuer/token_endpoint/audience/auth_methodを取得します。
4. 以下のJWTを登録鍵で署名し、token_endpointへ送ります。JWT本体を記録・表示しません。

```json
{"iss":"<CLIENT_ID>","sub":"<CLIENT_ID>","aud":"<TOKEN_ENDPOINT>","iat":<現在のUnix秒>,"exp":<現在のUnix秒+30>,"jti":"<一回限りのUUID>"}
```

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=client_credentials&client_id=<CLIENT_ID>&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion=<SIGNED_JWT>
```

5. access_tokenで POST /v2/service/activate に {} を送ります。その後、許可済みservice queryを実行します。serviceのaccess tokenは最大300秒。更新は新しいjtiによるclient_credentials取得です。人用refresh tokenの流用はしません。
6. suspend/revoke後は旧JWTの拒否を確認します。resume後も古いJWTを再利用せず、状態に応じてprovision、新規token、activateを行います。変更APIは最新versionを要求します。

## OpenAPIツールへ接続する

公開OpenAPIのserversとOIDC/OAuth URLは接続不能な説明用example.invalidです。公開ファイル自体へ本物の接続情報を書き込まず、[環境版生成ツール](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/configure-openapi.py)と[接続情報の雛形](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/environment.example.json)でローカルの環境版を作成します。

```sh
python configure-openapi.py --source openapi.json --profile environment.json --output openapi.environment.json
```

生成したファイルを対応ツールに読み込み、本人用はPKCE対応のOIDC認証と登録済みclient_id/redirect_uriを設定します。service用のprivate_key_jwtは汎用Swagger UIのclient_secret欄では代替できません。ホストの署名・秘密管理で取得したaccess tokenをBearerへ渡します。環境版は顧客接続情報を含むため公開repoへ置かないでください。

## 権限・本人・AI

actorはCoreが資格から解決する内部本人IDです。ヘッダーで任意のactorやroleを名乗れません。管理者のcan_manage_accessと表のread/write/designは別の権限です。表・列・行・期限は各操作で再検査します。

本人を支援するAIは本人と呼出しサービスの関係を維持します。MCPのreadOnlyHintやツール名は権限の付与ではありません。[MCP](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html)と[BFFの運用](https://mxd2024.github.io/claudia-partner-docs/v0.7/operations.html)を参照してください。
