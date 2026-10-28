# service として接続する

serviceは、人の操作なしに動く処理（バッチや連携など）が、基盤に接続するための方式です。利用者がログインする方式（[利用者として接続する](authentication.md)）とは、別の方式です。

serviceは、組織の管理者の承認を受けて、動きます。承認された、表、列、操作、期限の範囲だけで動き、それを超えることはできません。

## 登場するもの

- **あなたのサーバー処理**: serviceとして動く処理です。登録した鍵を持ちます。
- **組織の管理者**: serviceを申請の内容どおりに承認し、使える状態にします。
- **認証サービス**: 署名された要求を確認して、serviceにトークンを発行します。
- **基盤**: トークンを確認し、承認された範囲で、APIを実行します。

## 全体の流れ

1. あなたが、申請の内容（公開鍵を含む）を決めます。組織の管理者が、serviceの利用を申請します。
2. 組織の管理者が、申請を承認し、使える状態（provision）にします。
3. あなたのサーバー処理が、秘密鍵で署名した要求を、認証サービスに送り、トークンを受け取ります。
4. 初めて使うときに、有効化（activate）を行います。
5. トークンを付けて、許可された操作を呼びます。

## 前提

この手順は、`managed`方式のserviceを対象にします。申請、承認、provisionには、MFAを完了した管理者（`manage_access`と`service_administrator`の両方を持つ利用者）が必要です。申請者と承認者を分ける仕組みは、強制されません。業務の運用で分ける場合は、別に決めてください。利用者のJWTは、serviceのactivate、metadata、query、batch、importには使えません。各経路には、専用のservice JWTを使います。

- 環境管理者から、接続情報を受け取っていること。
- 組織の管理者が、MFA付きの利用者の資格で、service-clientsを操作できること。
- 秘密鍵は、あなたのサーバー処理だけが持ちます。申請には、公開鍵（JWK）だけを渡します。RSA 2048〜4096ビット、RS256、`kid`付きの鍵を使います。秘密鍵を、API、MCP、チャットへ送らないでください。

## 申請から利用まで

1. **申請する（組織の管理者。申請の内容は、あなたが決めて、管理者に渡します）。** `POST /v2/service-clients`に、`Idempotency-Key`（UUID）を付けて、`app_id`、`purpose`、`expires_at`、`rpm`、`jwk`、`scopes`を送ります。期限は最大90日、`rpm`（1分あたりのリクエストの上限）は1〜120です。`scopes`には、表、`schema_version`、読む列、書く列、操作、行を明示します。`create`を許可するときは、`custodian`も設定します。本文の例は、下の「申請の本文の例」にあります。
2. **承認する（組織の管理者）。** 返ったclient idと`version`を使い、`POST /v2/service-clients/{clientId}/approve`に`{"version":現在の版}`を送ります。
3. **provisionする（組織の管理者）。** 最新の`version`で、`/provision`を実行します。`ready`の状態と、接続の情報（issuer、`token_endpoint`、audience、`auth_method`）を取得します。
4. **トークンを取得する（あなたのサーバー処理）。** 次のJWT（署名付きの要求）を、登録した鍵で署名し、`token_endpoint`へ送ります。JWTの本体は、記録も表示もしません。`iss`と`sub`、およびフォームの`client_id`には、応答の`client_id`（文字列）を使います。2〜3の、パスの`{clientId}`には、応答の`id`（UUID）を使います。2つは別の値です。

```json
{"iss":"<CLIENT_ID>","sub":"<CLIENT_ID>","aud":"<TOKEN_ENDPOINT>","iat":<現在のUnix秒>,"exp":<現在のUnix秒+30>,"jti":"<一回限りのUUID>"}
```

```http
POST <token_endpoint> HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=client_credentials&client_id=<CLIENT_ID>&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion=<SIGNED_JWT>
```

5. **activateする（あなたのサーバー処理）。** provisionが返す`audience`は、取得するアクセストークンの宛先（API）で、JWTの`aud`（`token_endpoint`）とは別の値です。JWTのヘッダーの`kid`は、登録した公開鍵の`kid`と一致させます（RS256）。 `access_token`で、`POST /v2/service/activate`に`{}`を送ります。serviceの`access_token`の有効期間は、最大300秒です。更新は、新しい`jti`で、`client_credentials`を取得し直します。利用者用のリフレッシュトークンは、使いません。
6. **使う（あなたのサーバー処理）。** 許可された`POST /v2/service/tables/{collection}/query`を実行します。

**期待する結果**: 許可された操作が、200で成功します。`GET /v1/me`は、人の利用者の専用なので、拒否されます。利用環境の認証の入口によって、401（`TOKEN_INVALID`）または403のどちらかになります。実際のHTTPとcodeを記録してください。「人として接続できた」ことを、成功の条件にしないでください。

### 申請の本文の例

```json
{
  "app_id": "work-time-reader",
  "purpose": "ケースごとの作業時間の集計。金額は読まない",
  "expires_at": "<現在から90日以内のUTCの日時>",
  "rpm": 60,
  "jwk": {"kty":"RSA","n":"<生成したRSA公開鍵のbase64urlの値>","e":"AQAB","kid":"work-time-reader-key-1","alg":"RS256","use":"sig"},
  "scopes": [{
    "collection": "work_log", "schema_version": 1,
    "read": ["department","duration","case_number"],
    "write": [], "operations": ["query"],
    "rows": {"kind":"match","values":{"department":"production"}}
  }]
}
```

`<…>`の箇所は、実際の値に置き換えます。`jwk`には公開鍵の要素だけを入れます。秘密鍵の要素（`d`・`p`・`q`・`dp`・`dq`・`qi`）を含めると、400で拒否されます。JWKのURLは受け付けません。1つのserviceに許可できる表は、16までです。

## metadataと取込の経路

文書対象の固定仕様には、`GET /v2/service/tables/{collection}`（`service.metadata`）と`POST /v2/service/tables/{collection}/import`（`service.import`）が追加されています。ともにservice専用で、利用環境の対応版と有効化が必要です。

取込本文は`schema_version`、`expected_actor`、`operations`に従い、`Idempotency-Key`を指定します。権限は現在のservice承認範囲で判定します。通常のbatchや人用importから、本文・認証・上限を流用しないでください。[APIリファレンス](../openapi.json)で現在の型と条件を確認します。これらの追加を、利用中の利用環境で実機確認済みとは扱いません。

## 世代と再開

初めて使うときは、provisionの後、service専用のアクセストークンで、activateします。rotate（鍵の更新）の後と、suspendからresumeの後も、新しい世代を反映するために、provisionとactivateが必要です。古い世代の資格は、使えません。revokedは、元に戻りません。

## 権限の範囲（scopes）

`rows`は、`{"kind":"all","values":{}}`で、すべての行です。`{"kind":"match","values":{…}}`は、指定した列の値が一致する行で、複数の列は、すべての一致（AND）が条件です。任意の条件式では、ありません。`custodian`は、createした行を保管する責任者の、有効な利用者のUUIDで、createを許可するときに、必要です。実行の主体は、監査の上でも、serviceのままです。利用者になりすますものでは、ありません。

## 権限の変更

serviceの権限（表、列、操作）は、`PUT /v2/service-clients/{clientId}/permissions`で、**全置換**で更新します。省略した表、列、操作は、許可から外れます。有効なserviceは、同じJWTのままで、次のリクエストから、新しい設定に従います。通常の設定変更で、provisionやactivateを、やり直す必要はありません。

## 期限を延ばす

serviceの期限（`expires_at`）は、設定する時点から90日以内です。組織の管理者の管理権限の期限と、利用環境の契約の期限・利用期間の期限も、超えられません。

続けて使うときは、期限が来る前に、組織の管理者が`PUT /v2/service-clients/{clientId}/permissions`で、`GET /v2/service-clients/{clientId}`で得た最新の`version`と、新しい`expires_at`を送ります。この操作は全置換なので、今の`rpm`と`scopes`も、そのまま送ります。有効なserviceは、同じJWTのまま、次のリクエストから新しい期限に従います。provisionやactivateのやり直しは要りません。

鍵の更新（rotate）では、期限は延びません。期限を過ぎると、serviceのリクエストは401（`TOKEN_INVALID`）で拒否され、鍵の更新（rotate）・provision・resumeの管理の操作も、401（`TOKEN_EXPIRED`）で拒否されます。

## 定時の集計・同期

基盤のAPIには、決まった時刻に処理を動かす操作はありません。毎日の集計や、ほかのシステムとの同期は、お客さまのアプリのサーバー（BFF）が、決めた時刻に、serviceとして読み書きします。

- 集計の操作（`POST /v2/tables/{collection}/aggregate`）は、利用者のログインで使う操作で、serviceでは使えません。serviceでは、`query`で必要な行を読み、アプリで集計します。
- `query`は、1回199行まで（指定しないときは50行）です。応答の`next_after`を、次の`after`に渡して、続きを読みます。行は行のIDの順で返ります。読み終えるまでの間に、ほかの更新が入ることがあります。`filter`と`sort`は使えません。
- `batch`は、1回50操作まで、本文は64KiBまでです（人の`batch`の100操作とは違います）。取込（`import`）は、1回100操作・256KiBまでです。
- 1分あたりのリクエストは、申請の`rpm`（1〜120）までです。超えると、429（`RATE_LIMITED`）で拒否されます。認証を通り、上限の内で受け付けたリクエストは、そのあと拒否されても、数に入ります。認証できないリクエストと、上限で断られたリクエストは、数に入りません。
- 1行の値は、16KiBまでです。serviceで行を作るときは、表の行が25,000行に達していると、作れません（413 `PAYLOAD_TOO_LARGE`）。
- 利用者のログインで使う検索と集計は、利用者が見られる範囲の全体が25,000行・32MiBのどちらかを超えると、使えません（[表とデータの更新](tables.md)の「上限」）。

## 使い始める前に

- serviceを使うには、その利用環境で、serviceの経路を有効にする必要があります。初めて使うときは、Claudia Partnerサポート（[サポートと窓口](support.md)）に知らせてください。
- アプリのサーバーは、自分の名前と版のUser-Agent（例: `ExampleApp/1.0`）を付けて、リクエストを送ります。言語やライブラリの既定の名乗りのままだと、基盤に届く前の入口で断られることがあります（HTTP 403、`text/plain`、本文が`error code: 1010`。[MCPの対応範囲とトラブル対応](mcp-support.md)の「接続できないとき」）。ブラウザーなど、ほかのソフトウェアの名乗りをまねないでください。

## 断られるときの答え

| 場面 | HTTP | `code` |
| --- | --- | --- |
| 許可した範囲（`scopes`）にない表 | 404 | `NOT_FOUND` |
| 行の条件（`rows`）に合わない行の更新・削除 | 404 | `NOT_FOUND` |
| 許可していない操作（例: `query`だけを許可した表への`batch`） | 403 | `FORBIDDEN_ROLE` |
| 許可していない列への書き込み | 403 | `FIELD_NOT_WRITABLE` |
| 書いた結果の行が、行の条件から外れる | 403 | `SCOPE_VIOLATION` |
| provisionの後、activateの前 | 403 | `FORBIDDEN_ROLE` |
| provisionの前、停止（suspend）・失効（revoke）・期限の後、rotateの後の古い世代のトークン | 401 | `TOKEN_INVALID` |
| 許可の`schema_version`と、表の今の版が違う | 409 | `STATE_CONFLICT` |
| 行の`version`が今の版と違う | 412 | `VERSION_CONFLICT` |
| 1分あたりの上限を超えた | 429 | `RATE_LIMITED` |

## 停止と失効

suspend（一時停止）またはrevoke（失効）の後は、古いJWTが拒否されることを確認します。resume（再開）の後も、古いJWTを再利用しません。状態に応じて、provision、新しいトークンの取得、activateを行います。変更のAPIは、最新の`version`を要求します。

## 次に

許可された範囲での読み書きは、[表とデータの更新](tables.md)。通しの手順は、[アプリの登録と運用](tutorial.md)。
