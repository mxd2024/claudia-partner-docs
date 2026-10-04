# 最初のAPI接続

対象は API 0.7.0-experimental。初回は人の本人資格で GET /v1/me の200を確認します。service用資格では、人用APIへの拒否が正しい動作です。

## 1. 接続情報を受け取る

環境管理者へ「開発接続情報と検証用データ」を依頼し、次を確認してください。これらを公開資料から推測しません。

| 項目 | 必要な値 |
| --- | --- |
| Core | HTTPS origin、API版、有効モジュール |
| IdP | issuer、discovery URL、認証方式、必要なMFA |
| 本人用クライアント | 登録済みclient_id、redirect_uri、scope、対象audience |
| 本人 | ログイン方法、利用組織、必要な表利用権 |
| 検証用表 | collection、現在schema_version、許可する操作、検証行 |
| 証明書 | 公開CA、または管理者が交付した検証CAと照合用SHA |

Core、顧客アプリ/BFF、IdPは別の接続先です。インターネット上の本サイトは仕様の配信先で、APIサーバーではありません。

## 2. 本人のaccess tokenを取得する

[認証手順](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html)のAuthorization Code + PKCEを実施します。通常は提供された顧客アプリ/BFFのログインを利用し、資格はそのBFFが保持します。直接APIを試す開発用クライアントは、事前に登録済みのredirect_uriを使います。ID tokenをAPI資格として送らないでください。

## 3. GET /v1/meを呼ぶ

[完全なHTTP例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)の「本人を確認」を利用します。Authorizationは取得したaccess_tokenに置換します。200と本人id、permissions、capabilities、sessionの期限を確認します。返る権限配列が空でも本人確認の成功であり、表操作の許可を意味しません。

401ならissuer・audience・client・期限・セッションを確認し、403なら現在権限とMFAを確認します。署名検査や認可を無効にして接続を通しません。

## 4. 表一覧から検索へ

v1表は GET /v1/tables、v2表は GET /v2/tables を使います。一覧で得たcollectionのdefinitionを取得し、読み取れる列・検索可能な列・schema_versionを確認してqueryへ進みます。[表の操作](https://mxd2024.github.io/claudia-partner-docs/v0.7/tables.html)、[実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)、[通し手順](https://mxd2024.github.io/claudia-partner-docs/v0.7/tutorial.html)を参照してください。

## service接続の場合

管理者の申請・承認・provision後、private_key_jwtでclient_credentialsを取得します。初回activate後に許可済み POST /v2/service/tables/{collection}/query の200を確認します。GET /v1/meは人専用のため拒否を確認します。環境の認証入口により401 TOKEN_INVALID、または403の認可拒否になり得るため、実際のHTTPとcodeを記録します。人として接続できたことを成功条件にしません。

## 文書版と検証範囲

[manifest](https://mxd2024.github.io/claudia-partner-docs/v0.7/../manifest.json)で公開ファイルを照合できます。文書の例は合成データです。各環境の初回接続、macOS実機、独立した利用者による通し受入の結果は、文書の静的検査とは別です。[対応状況](https://mxd2024.github.io/claudia-partner-docs/v0.7/versions.html)で未確認を確認してください。
