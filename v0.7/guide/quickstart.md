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

## ログイン直後の反映待ち

新しい本人セッションは収集・DB反映の完了まで GET /v1/me が401 TOKEN_INVALIDになる場合があります。現collectorは**1回の処理完了後に15秒待機**します。固定15秒周期ではなく、収集・DB処理時間が加わります。外部収集に28秒の期限はありますが、全工程を包含する期限ではありません。**ログインから利用可能になるまでの保証上限・SLAは未定義**です。15秒、28秒、43秒以内の成功を保証しません。

正常に完了した新規ログイン直後で、同じ資格の GET /v1/me だけがTOKEN_INVALIDの場合に限り、回数と経過時間を限定して待機できます。クライアント待機枠の例は0.5秒間隔・最大20秒です。これは成功保証ではありません。20秒を超えたら待機を終了し、時刻・code・request_idを記録して環境管理者へ確認します。全401や変更操作を自動再送する規則ではなく、TOKEN_EXPIRED、明示失効、403、TLS/署名エラーには適用しません。

Coreのchecked_atの鮮度は5秒以内、reconciled_atは60秒以内を要求します。これらは古い認可情報を拒否する条件であり、新セッションの反映時間の約束ではありません。

## 接続情報の依頼窓口

窓口の担当者、受付手段、受付時間、発行の目標時間は**責任者による決定待ち・未確定**です。暫定的に環境管理者へ、用途・接続対象環境・本人/サービスの区分・希望する操作と表・client_id/redirect_uri・希望期限・返答先を伝えてください。この一覧は依頼項目であり、受付済み・発行期限の保証ではありません。
