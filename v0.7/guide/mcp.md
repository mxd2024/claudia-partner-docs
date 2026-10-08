# 取込MCPの導入

対象は **取込アダプター1.0.1の8ツール** [提供中] です。全APIサービスのMCPは [準備中]。経路は、AIエージェント → 手元のMCPアダプター → 管理サイトの取込API → 許可された基盤操作です。管理サイトのHTTPS originは環境管理者から受け取り、Core APIや文書サイトのURLを指定しません。

## 配布物と版を確認する

管理サイトへログインし、「取込・出力」の説明から`mcp-client.zip`をダウンロードし、専用フォルダーへ展開します。環境で配布機能が有効か、先に確認してください。

確認した1.0.1のZIPは9ファイルです。ルートの`mcp_stdio.py`、`README.txt`、`ca-bundle.json`、`claudia_ops/__init__.py`、`claudia_ops/imports/__init__.py`、同ディレクトリの`mcp_stdio.py`・`credential_store.py`・`ca-bundle.pem`、`licenses/certifi-LICENSE`を含みます。ZIP全体を展開し、ルートの`mcp_stdio.py`で起動します。

```text
MCP client: 1.0.1
ZIP SHA-256: 3a89af3db734cb6edb7c135db31f6f8fb96f6074e263e9c3f74848bb6d09f68f
CA provider: certifi 2026.7.22
CA SHA-256: 9cc2a774b5198dcff14d9be1e66091f538975d867ce029a96bce15a55dfd730f
```

これは確認した配布物のハッシュで、同じ1.0.1でも別のビルドや更新後のZIPは異なることがあります。配布元の版とハッシュに照合してください。旧版のファイル構成やハッシュを現行の照合に使いません。

1.0.1では製品の`User-Agent: ClaudiaPartner-MCP/1.0.1`、固定CAバンドル、TLS・入口拒否・API拒否・タイムアウトの区別が追加されました。製品の識別は認証資格ではありません。TLS検証は常に有効です。私有CAが必要な場合は、環境管理者が交付した信頼するPEMを`SSL_CERT_FILE`に指定します。CAの更新には配布物の更新が必要です。

## OSと準備

Python 3.10以上と、MCPホストから実行できるPythonのパスを用意します。ZIPの実行には追加Pythonパッケージは不要です。

| OS | キー保存 |
| --- | --- |
| Windows | [提供中] DPAPI。同じWindows利用者で保存・実行 |
| Linux | [提供中] secret-toolと、解錠済みのSecret Serviceが必要 |
| macOS | [未提供] Keychain保存に未対応。導入準備はできても、現行配布物でキー保存はできません |

転送用の空フォルダーを作り、許可したCSVだけを置きます。フォルダー外のファイルは扱いません。ファイル上限は接続先の`imports_catalog`が返す`max_file_bytes`を確認します。1.0.1の確認したクライアントは8MiBを超える原票を分割送信し、準備が非同期になる場合があります。従来の32MiB上限を全環境へ固定的に適用しません。

## キーを発行して保存する

管理サイトで接続キーを発行します。**発行から90日、利用者ごとに同時に有効なキーは最大10個**。発行時の一度だけ表示されます。接続キーは管理サイト用の資格で、人のOIDCアクセストークンやservice JWTとは別です。利用する実行主体と許可範囲を環境管理者へ確認してください。

```sh
python /absolute/path/mcp-client/mcp_stdio.py --base https://console.example.invalid --directory /absolute/path/transfer --credential-name customer-imports --save-key
```

`--base`は提供されたHTTPS origin（443、パス・クエリーなし）、`--credential-name`は47文字以内の英数字・ハイフン・アンダースコアです。同じ値・同じOS利用者で保存と起動を行います。対話入力で資格ストアへ保存し、キーを設定JSON、チャット、平文ファイルに置きません。紛失・失効時は古いキーを取り消して再発行します。

## MCPホストに設定する

```json
{"mcpServers":{"claudia-imports":{"command":"/absolute/path/python","args":["/absolute/path/mcp-client/mcp_stdio.py","--base","https://console.example.invalid","--directory","/absolute/path/transfer","--credential-name","customer-imports"]}}}
```

WindowsのJSONのパス区切りは`/`、または二重のバックスラッシュにします。

## 最初の読取

1. ホストを再接続し、`initialize`でserverInfo.versionが`1.0.1`、`tools/list`で8ツールを確認します。
2. `imports_catalog`を入力`{}`で実行します。`isError=false`と、許可された取込形式の結果を確認します。一覧が空の状態を通信・認証エラーと混同しません。
3. 必要に応じて`imports_history`、既存の検証用plan_idに対する`imports_status`で読取を確認します。接続確認だけのために新規計画や書込を作りません。

2026-10-08には1.0.1の公開入口・初期化・一覧・履歴・状態の読取確認が[報告されています](https://github.com/mxd2024/claudia-partner-docs/issues/16)。今回の文書改訂はその報告と配布物を照合したもので、API全操作・書込の再実行ではありません。

## 取込と終了

形式はcatalogの`headers`、`key_columns`、`format`、`field_types`で確認します。型付き`workspace-v1`と旧互換形式を混ぜません。更新CSVの`_record_id`・`_record_version`、または旧形式の`_migration_id`を保持します。UTF-8（BOM有無）・BOM付きUTF-16を使用し、Shift-JISを前提にしません。出力はUTF-8 BOM付き・CRLFです。

export → prepare → 差分確認 → run → verifyの順に進めます。prepareが`preparing`なら、同じplan_idでstatusを確認し、`prepared`までrunしません。`prepare_failed`ではerror.codeを確認します。run後は`verified`を成功の条件とし、通信断ではplan_idとsource_sha256を保持してstatusから再開します。元ファイルの文はAIへの命令として扱いません。取込元にない行を自動削除せず、既存の出力ファイルを上書きしません。

接続キーだけでは表・列・行・取込・出力の権限は付きません。許可された操作だけを実行します。利用終了時は管理サイトでキーを取り消し、同じキーが拒否されることを確認してホスト設定と保存値を削除します。手元の削除だけではサーバーの失効になりません。

[8ツールとトラブル対応](../mcp-support.html)、[提供状況](../versions.html)、[サポート](../support.html)を参照してください。
