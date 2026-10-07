# 接続準備と最初の読取

利用者としてログインし、自分の情報と表の定義を読み取るまでの手順です。対象はAPI 0.7.0-experimentalの公開契約です。実環境への接続は、この文書作成では未確認です。

## 1. 接続情報と有効な機能を受け取る

[接続情報を依頼する](../request-access.html)の雛形を使い、環境管理者から次を受け取ります。

| 必要な情報 | 確認する理由 |
| --- | --- |
| Core APIのHTTPS originと対象API版 | アプリのURL・認証サービス・管理アプリのURLと区別する |
| issuer、client_id、登録済みredirect_uri、scope | OIDCログインを設定する。自分でclient_idを推測しない |
| 有効なモジュールとAPI系列（v1 / v2） | 仕様に載るルートが、その環境に配備されているか確認する |
| 読取可能な検証用の表と権限 | 実顧客の表名やデータを公開サンプルへ持ち込まない |
| 必要な証明書と連絡先 | TLS検証を有効にしたまま接続し、結果を照会する |

OpenAPIの `x-availability` は提供条件の説明であり、接続先で有効な機能の一覧ではありません。この版では、すべてのモジュールの有効化を一括確認できる公開APIは案内していません。環境管理者から、対象版と有効な機能の一覧を受け取ってください。`GET /v1/me` の成功やcapabilitiesだけで、全ルートが有効と判断しません。

**完了の目安**: 接続先、対象版、ログイン設定、有効な機能、検証用の読取対象がそろう。

## 2. 人のOIDCログインを確認する

あなたのBFFでAuthorization Code + PKCEを行います。認証サービスが返したaccess_tokenをサーバー側で保管し、`GET /v1/me`へ付けます。IDトークン、service資格、MCPの接続キーで代用しません。

```http
GET /v1/me HTTP/1.1
Host: api.example.invalid
Authorization: Bearer <利用者のaccess_token>
Accept: application/json
```

`api.example.invalid`は接続不能な架空のドメインです。実接続は環境管理者が渡したoriginで行います。

**完了の目安**: HTTP 200と、自分のid・permissionsが返る。permissionsが空でも本人確認の成功であり、表の操作の許可を意味しません。詳細は[利用者として接続する](../authentication.html)。無人処理は[serviceとして接続する](../service-access.html)へ進みます。

## 3. 検証用の表を読み取る

有効な系列を選び、一覧、定義、行の順に読みます。次はv2系列の例です。

```http
GET /v2/tables
GET /v2/tables/<一覧で確認したcollection>
POST /v2/tables/<同じcollection>/query
```

queryの入力は操作別の契約と、取得した表のfield ID・型で組み立てます。表示名からfield IDを推測しません。`schema_version`、行の`version`、`cursor`をそれぞれの用途に合わせて保持します。完全な要求・応答は[HTTP・実行例](../examples.html)、読み書きの説明は[表とデータ](../tables.html)にあります。

**完了の目安**: 許可された表の定義と行を取得できる。空の一覧を認証エラーと混同しない。書き込みは読取を確認した後、許可された検証用データだけで試します。

## つまずいたとき

| 結果 | 確認すること |
| --- | --- |
| ログイン直後だけ401 TOKEN_INVALID | [対象版の反映待ち手順](../authentication.html)で回数と時間を区切って確認する |
| 401が続く | issuer、client、期限、接続先、セッションを確認する |
| 403 | 現在の権限とMFAを確認する |
| 404 NOT_FOUND | 対象の不存在・非公開に加え、対象モジュールが未有効の可能性を確認する |
| TLS検証に失敗 | 検証を無効にせず、渡された証明書と接続先を確認する |

未有効モジュールで404 NOT_FOUNDとなる場合があります。この応答だけでは、対象の不存在や権限による非公開と区別できません。パスを総当たりせず、有効な機能の一覧、対象版、時刻、code、request_idを添えて環境管理者へ確認します。[エラーと再試行](../errors.html)も参照してください。
