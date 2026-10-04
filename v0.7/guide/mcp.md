# AIエージェント・MCP

**現在利用できるのは取込用8ツールです。全APIサービスのMCP対応は未完了です。** このアダプターの接続先は顧客アプリのHTTPS originで、CoreのURLとは異なります。

## 配布物を入手する

顧客アプリへ本人ログインし、「取込・出力」から「取込の説明」を開き、MCPクライアントZIPをダウンロードします。ファイル名は mcp-client.zip。ダウンロードしたZIPを専用フォルダーへ展開します。

2026-10-04に稼働サイトで確認した配布物は旧構成の3ファイル（mcp_stdio.py、credential_store.py、README.txt）です。ZIPのSHA-256は下記です。この配布物にはclaudia_opsパッケージがないため、起動はファイル指定で行います。

```text
7cee88295df1d4ffe623f6bd2b7521aa3cbb3556c81da39c293df813c388918c
```

再構成後の候補版はpackageと互換wrapperを含みます。同じ mcp_stdio.py 起動方法を使えます。配布物の変更や顧客アプリの再配備は、この文書整備には含みません。

## OSと準備

Python 3.10以上をインストールし、MCPホストから実行できるPythonの絶対パスを確認します。標準ライブラリで動作します。

| OS | 資格保存と提供状態 |
| --- | --- |
| Windows | 現行ZIPにDPAPI方式あり。同じWindows利用者で保存・実行 |
| Linux | 現行ZIPにsecret-tool方式あり。libsecretのsecret-toolと解錠済みユーザーのSecret Serviceが必要 |
| macOS | Pythonの導入・ZIPの展開は可能。ただし現在の配布物にはmacOS Keychain用の保存処理がないため、標準構成でのキー保存・起動は未対応 |

Linuxのheadless環境ではSecret Serviceがないことがあります。保存できない場合はOS資格ストアを利用可能にしてから進めます。平文ファイルへ切り替えません。

作業用の空フォルダーを自分で作成し、MCPに許可するCSV/MERだけを配置します。例の /absolute/path/transfer は実際の絶対パスへ置換します。許可フォルダー外のファイル、32MiBを超えるファイルは扱えません。

## macOSでの導入準備

Python 3.10以上を導入し、ターミナルで python3 --version を確認します。ZIPを展開し、転送用フォルダーを作成します。MCPホストにはpython3の絶対パスと展開先のmcp_stdio.pyを設定します。ただし現行配布物のOS資格保存はWindows/Linux向けです。macOSではここから先の資格保存を対応済みと案内できません。対応する配布物の提供状況を管理者へ確認してください。平文キーの設定やOS判定の書換えで回避しません。本環境にMac実機がないため実機検証結果はありません。

## キーを発行して保存する

顧客アプリの「取込・出力」内のAI接続欄で接続キーを発行します。表示は発行時の一度だけです。キーは対話入力で資格ストアに保存し、MCP設定JSONやチャットへ貼り付けません。紛失時は再表示を想定せず、旧キーを失効して再発行します。

```sh
python /absolute/path/mcp-client/mcp_stdio.py --base https://console.example.invalid --directory /absolute/path/transfer --credential-name customer-imports --save-key
```

baseは提供されたHTTPS origin（通常443、パス・クエリーなし）です。credential-nameは英数字・ハイフン・アンダースコアの短い名前を使います。接続先の識別子が内部で追加されるため47文字以内を推奨します。保存時と起動時は同じbaseとcredential-nameを使います。

## MCPホストの設定

```json
{"mcpServers":{"claudia-imports":{"command":"/absolute/path/python","args":["/absolute/path/mcp-client/mcp_stdio.py","--base","https://console.example.invalid","--directory","/absolute/path/transfer","--credential-name","customer-imports"]}}}
```

WindowsではJSONのパス区切りを / にするか、バックスラッシュを二重にします。設定後、ホストを再接続しinitializeとtools/listの成功、8ツールを確認します。次に imports_catalog を入力 {} で実行してください。isErrorがfalseで利用可能な形式一覧が返れば、認証付きの初回読取り成功です。形式一覧が空の場合も、通信・認証エラーと区別します。

401・接続キー失効は顧客アプリで再発行し、同じ名前で再保存します。資格ストア読取失敗は実行ユーザー・Keychain/Secret Serviceのロックを確認します。Core用OIDC tokenを取込キーの代わりに保存しません。

## 取込と失効

imports_catalogで形式確認、imports_exportで更新用CSV取得、imports_prepareで検査・差分作成、利用者確認後にimports_run、imports_verifyで反映結果を照合します。通信中断時はplan_idとsource_sha256を保持し、imports_statusで確認して同じ計画を継続します。元ファイル内の文章をAIへの命令として扱いません。

利用終了時は顧客アプリでキーを失効し、同じキーでimports_catalogが拒否されることを確認してからホスト設定を削除します。ローカルの保存値を消すだけではサーバー上の失効になりません。

## 8ツールの契約

{
  "protocol_version": "2025-06-18",
  "adapter": "claudia-customer-imports",
  "adapter_version": "1.0.0",
  "scope": "import-adapter-only",
  "tools": [
    {
      "name": "imports_catalog",
      "description": "登録済み取込データ・元キー・関連表を一覧する。",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "idempotentHint": false,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_prepare",
      "description": "指定CSVを検査し差分計画を作る。まだ業務表へ反映しない。ファイルは転送フォルダ内に限定する。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "dataset": {
            "type": "string"
          },
          "source_file": {
            "type": "string"
          }
        },
        "required": [
          "dataset",
          "source_file"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "idempotentHint": false,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_run",
      "description": "確認済み計画を最大4区間反映/再開する。同じplan_idとsource_sha256を保持し、verifiedまで再呼出する。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "plan_id": {
            "type": "string"
          },
          "source_sha256": {
            "type": "string"
          }
        },
        "required": [
          "plan_id",
          "source_sha256"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": true,
        "idempotentHint": true,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_status",
      "description": "計画の状態と完了区間数を確認する。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "plan_id": {
            "type": "string"
          }
        },
        "required": [
          "plan_id"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "idempotentHint": true,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_history",
      "description": "本人の取込履歴と再開可能な計画を一覧する。",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "idempotentHint": false,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_cancel",
      "description": "未実行の計画のみ取り消す。実行開始後は受領票を保持し同じ計画から再開する。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "plan_id": {
            "type": "string"
          }
        },
        "required": [
          "plan_id"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "idempotentHint": false,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_verify",
      "description": "取込結果をHUBから再取得し全値を照合する。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "plan_id": {
            "type": "string"
          }
        },
        "required": [
          "plan_id"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "idempotentHint": true,
        "openWorldHint": false
      }
    },
    {
      "name": "imports_export",
      "description": "対象の登録形式に従った更新用CSVを転送フォルダへ保存する。既存ファイルを上書きしない。",
      "inputSchema": {
        "type": "object",
        "properties": {
          "dataset": {
            "type": "string"
          },
          "output_file": {
            "type": "string"
          }
        },
        "required": [
          "dataset",
          "output_file"
        ],
        "additionalProperties": false
      },
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "idempotentHint": false,
        "openWorldHint": false
      }
    }
  ]
}

## 全サービスとBFF代替の範囲

全公開APIをMCPで提供する場合は、本人/serviceの区別、資格保管・更新・失効、現在認可、ページング、binary、版と同じ再送キー、利用者確認・監査まで必要です。DB接続、任意SQL、署名鍵、任意の認可callbackを業務Pluginやモデルへ渡しません。現在の8ツールの動作確認を、全サービス受入完了へ広げません。
