# HTTP・実行例

60の例（全134操作のうち56操作）を載せています。すべて合成データのリクエストと応答です。実際の利用環境での実行結果ではなく、実機動作は未確認です。HTTPヘッダーとJSONは[共通examples JSON](examples/public-requests.json)から生成し、OpenAPIのexamplesにも同じ内容を使用します。時刻、UUID、版、fingerprint、storeは説明用です。実行時には現在の取得結果へ置き換えてください。

成功応答の値は固定の期待値ではありません。表の権限や現在版に従い変化します。公開資料は検証用のデータ投入を自動的に行いません。[アプリの登録と運用](tutorial.html)に沿い、検証専用の表で実行してください。

## サンプルアプリ

架空の作業メモを使って、APIの組み合わせを説明します。完成した配布アプリではなく、実装を考えるための例です。顧客の実データは含みません。説明どおりの実機動作は未確認です。

### 表と権限

表`demo_tasks`に、text型の`title`（件名）を定義します。まずはこの1列で読み書きを確認します。担当者・顧客・連絡先を管理する業務や、特定のOS・配置先を前提にしません。表を作るには事前の設計権限、行の読み書きには対象の表と列の権限が必要です。

### 接続と読み取り

ブラウザー → アプリのサーバー側（BFF）→ 基盤APIの構成を例にします。人のログインは認証サービスのOIDC Authorization Code + PKCEとMFAを使います。登録済みclient_id等が必要で、個別アプリの登録・BFF接続は準備中です。

1. [接続情報](request-access.html)と利用環境の有効機能・稼働版を確認します。
2. [本人として接続](authentication.html)し、`GET /v1/me`を確認します。
3. 表のdefinitionから`schema_version`を取得します。
4. `POST /v2/tables/{collection}/query`で、許可された作業メモを読みます。空の一覧と認証エラーを区別します。

### 作成・更新・競合

[HTTP・実行例](examples.html)の`v2-create`、`v2-query`、`v2-update`を参照します。新規作成のidはサーバーが決めます。更新には取得したid・versionと現在のschema_versionを使い、操作ごとにIdempotency-Keyを作ります。

412なら最新値と編集内容を比較して利用者に確認します。通信が途切れただけなら、同じキーと本文を保持して結果を確認し、別キーで二重に更新しません。[競合・再送・復帰](reliability.html)を参照してください。

### 画像と自動処理を追加する場合

画像を扱う場合は、別途asset_ref型の欄と利用環境のpolicyを確認します。外部参照の例は保存先`sample-files`内の`examples/sample-image.png`です。任意のURLやOSの絶対パスを保存しません。[画像とDropbox連携](media.html)を参照してください。

無人処理には承認済みserviceを使い、人のJWTを流用しません。MCPは管理サイトの接続キーで使う取込用8ツールです。人OIDC、service JWT、MCP接続キーは別々に管理します。

## サンプルの実行

[Python](examples/request.py)はPython 3.10以上の標準ライブラリ、[JavaScript](examples/request.mjs)はNode.js 22以上で動作します。どちらも選択した1リクエストのみを送信し、自動再試行しません。examples JSONを同じフォルダーへ保存して、置換済みのリクエストファイルを指定します。

```sh
python request.py --base https://api.example.invalid --request my-request.json
node request.mjs --base https://api.example.invalid --request my-request.json
```

資格は環境変数CP_ACCESS_TOKEN、またはPythonの非表示対話入力で渡します。スクリプトやリクエストファイルへ埋め込みません。CP_ACCESS_TOKENは[利用者として接続する](authentication.html)で取得したaccess_tokenです。baseは、環境管理者から受け取った、基盤のHTTPS originへ置き換えます。検証CAはPythonの --ca 引数、NodeのNODE_EXTRA_CA_CERTSで設定し、TLS検証を無効化しません。

my-request.jsonは下の共通JSONから1件を選び、headers内のAuthorizationプレースホルダー以外の値、url、bodyを実際の利用環境向けに直したものです。書込はIdempotency-Keyと期待版を確認してから実行します。

<!-- generated:http-examples -->

バイナリー例はbody_base64/response_base64で実バイトを表します。実行サンプルは送信時にdecodeし、バイナリー応答はbase64で表示します。JSON文字列を画像として送る形式ではありません。
