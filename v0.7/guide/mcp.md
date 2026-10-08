# MCPの導入

AIエージェントから、取込の操作を行うために、MCPアダプターを導入します。**文書対象は、クライアント1.0.1の取込用8ツールです** [環境による]。全APIサービスへの対応は [準備中] です。

現在の接続の経路は、AIエージェント → 手元のMCPアダプター → 管理サイトの取込API → インフラです。MCPアダプターの接続先は、管理サイトのHTTPS originで、インフラのAPIのURLとは異なります。管理サイトのoriginと利用条件は、利用環境ごとに確認します。接続キーは人OIDCのアクセストークンや、CoreAPIのservice JWTとは別の資格です。管理サイトからCoreAPIへの経路には、人セッションを使う構成と機械資格を使う構成があり、実際の構成と反映状態を確認してください。

## 配布物を入手する

管理サイトに利用者としてログインし、「取込・出力」から「取込の説明」を開き、MCPクライアントのZIPをダウンロードします。ファイル名は`mcp-client.zip`です。ダウンロードしたZIPを、専用のフォルダーへ展開します。

文書対象のZIP（1.0.1）には、起動用`mcp_stdio.py`、`README.txt`、`ca-bundle.json`、`claudia_ops/__init__.py`、`claudia_ops/imports/__init__.py`、`claudia_ops/imports/mcp_stdio.py`、`claudia_ops/imports/credential_store.py`、`claudia_ops/imports/ca-bundle.pem`、`claudia_ops/imports/licenses/certifi-LICENSE`の9ファイルが含まれます。起動は、`mcp_stdio.py`のファイルパスを指定して行います。ZIPのSHA-256は、次のとおりです。ダウンロードしたファイルが、同じ値であることを確認してください。

```text
3a89af3db734cb6edb7c135db31f6f8fb96f6074e263e9c3f74848bb6d09f68f
```

配布元で取得したファイルの版も確認してください。このハッシュは文書対象1.0.1の値で、配布元の最新ファイルと同一とは限りません。CAはcertifi 2026.7.22を同梱します。CAバンドルのSHA-256は`9cc2a774b5198dcff14d9be1e66091f538975d867ce029a96bce15a55dfd730f`です。

## OSと準備

Python 3.10以上をインストールし、MCPホストから実行できるPythonの絶対パスを確認します。標準ライブラリで動作します。

| OS | キーの保存と提供の状態 |
| --- | --- |
| Windows | [提供中] DPAPIで保存します。同じWindows利用者で、保存と実行を行います |
| Linux | [提供中] `secret-tool`で保存します。libsecretの`secret-tool`と、解錠済みのSecret Serviceが必要です |
| macOS | [未提供] Pythonの導入とZIPの展開はできますが、キーの保存（Keychain）に対応していません |

Linuxのheadless環境では、Secret Serviceがないことがあります。保存できないときは、OSの資格ストアを使える状態にしてから進めます。平文のファイルへ切り替えないでください。

作業用の空のフォルダーを自分で作り、MCPに許可するCSVだけを置きます。例の`/absolute/path/transfer`は、実際の絶対パスに置き換えます。許可したフォルダーの外のファイルは扱えません。1.0.1は8MiBを超えるCSVを分割して送信します。サーバーのファイル上限は`imports_catalog`の`max_file_bytes`を確認します。

## macOSでの導入準備

Python 3.10以上を導入し、ターミナルで`python3 --version`を確認します。ZIPを展開し、転送用のフォルダーを作ります。ただし、現在の配布物のキーの保存は、WindowsとLinux向けで、macOSではキーを保存できません。macOSに対応した配布物の提供状況は、[サポートと窓口](support.md)へ確認してください。平文のキーの設定や、OSの判定の書き換えで回避しないでください。

## キーを発行して保存する

管理サイトの「取込・出力」にある、AI接続の欄で、接続キーを発行します。キーが表示されるのは、発行したときの一度だけです。キーは、対話の入力で資格ストアに保存し、MCPの設定のJSONやチャットに貼り付けないでください。紛失したときは、再表示できません。古いキーを失効して、再発行します。有効期間は90日、利用者ごとの有効なキーは最大10個です。

```sh
python /absolute/path/mcp-client/mcp_stdio.py --base https://console.example.invalid --directory /absolute/path/transfer --credential-name customer-imports --save-key
```

`--base`は、提供されたHTTPS origin（通常は443。パスとクエリーなし）です。`--credential-name`は、英数字、ハイフン、アンダースコアの短い名前にします。47文字以内にしてください。保存のときと起動のときは、同じ`--base`と`--credential-name`を使います。

## MCPホストに設定する

```json
{"mcpServers":{"claudia-imports":{"command":"/absolute/path/python","args":["/absolute/path/mcp-client/mcp_stdio.py","--base","https://console.example.invalid","--directory","/absolute/path/transfer","--credential-name","customer-imports"]}}}
```

Windowsでは、JSONのパスの区切りを`/`にするか、バックスラッシュを二重にします。

## 接続を確認する

1. 設定の後、ホストを再接続し、`initialize`と`tools/list`が成功し、8ツールが見えることを確認します。
2. `imports_catalog`を、入力`{}`で実行します。
3. `isError`が`false`で、利用できる形式の一覧が返れば、認証付きの最初の読み取りが成功です。一覧が空のときも、通信や認証のエラーとは区別します。

2026-10-08の[公開検証記録](https://github.com/mxd2024/claudia-partner-docs/issues/16)では、初期化・一覧・catalog・history・statusの読取を確認しています。取込の書込と全環境の動作は未確認です。うまくいかないときは、[MCPの対応範囲とトラブル対応](mcp-support.md)。

## 取込の流れと、利用の終了

1. `imports_catalog`で、形式を確認します。
2. `imports_export`で、更新用のCSVを取得します。
3. `imports_prepare`で、検査と差分の作成を行います。`preparing`なら`imports_status`で待ち、`prepared`になった計画だけを実行します。`prepare_failed`なら入力とエラーを確認します。
4. 利用者が確認した後で、`imports_run`を実行します。
5. `imports_verify`で、反映の結果を照合します。

通信が途切れたときは、`plan_id`と`source_sha256`を保持し、`imports_status`で確認して、同じ計画を続けます。元のファイルの中にある文章を、AIへの命令として扱わないでください。

利用を終えるときは、管理サイトでキーを失効します。同じキーで`imports_catalog`が拒否されることを確認してから、ホストの設定を削除します。手元の保存値を消すだけでは、サーバー側で失効したことになりません。

## 取込のファイル（CSV）

- 読み取れる文字コードは、UTF-8（BOMの有無は問いません）と、BOM付きのUTF-16です。Shift-JISは、前提にしません。
- 出力は、UTF-8のBOM付きで、改行はCRLFです。
- 見出しの名前と順序は、`imports_catalog`が返す`headers`と、完全に一致させます。表のラベルから推測しません。
- 取込の形式は、`imports_catalog`の`format`で、最初に確認します。取込の形式は、アプリ定義と一緒に、`POST /v2/app-packages/plan`と`/apply`で、CSVの契約（`csv.key_fields`など）として登録します。登録は、管理者が行います。`imports_catalog`が空のときは、取込の形式が、まだ登録されていません。管理者または環境管理者に、確認してください。型付きの形式（`workspace-v1`）は、登録された必須のtext列を、照合のキー（`key_columns`）に使います。更新用の出力には、`_record_id`と`_record_version`の列が付くので、両方を保存します。旧互換の形式には、`_migration_id`と、別の照合の規則があります。2つを、混ぜないでください。
- 取込は、取込元にない行を、自動で削除しません。以前の照合の値と、現在の値が違う行は、競合として扱います。
- `source_file`と`output_file`の相対パスは、MCPアダプターを起動したときの`--directory`が基準です。絶対パスも、そのフォルダーの配下に解決されるものだけです。CSV以外のファイル、フォルダーの外、既存の出力ファイルは、拒否されます。元のファイルの上限は、現在の`imports_catalog.max_file_bytes`に従います。

## 必要な権限

接続キーだけでは、表の権限は付きません。人セッションを使う経路では、基盤が現在のセッション、表・行・列の権限、取込の権限（`can_import`）、登録された取込の形式を確認します。機械資格を使う経路では、管理サイトがキー所有者に許可されたdatasetを確認し、CoreAPIがserviceの現在状態・期限・表・列・行・操作の承認範囲を確認します。機械経路に人のJWTを流用しません。出力（export）には、出力の権限が、別に必要です。権限が足りないときは、環境管理者に、依頼してください。
