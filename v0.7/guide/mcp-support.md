# MCPの対応範囲とトラブル対応

## 対応範囲

**取込アダプター1.0.1、8ツール** [提供中]。全APIサービスのMCPは [準備中]。DB直接接続、任意のSQL、署名鍵の交付は提供範囲に含みません。導入は[MCPの導入](mcp.md)へ。

serviceの`GET /v2/service/tables/{collection}`と`POST /v2/service/tables/{collection}/import`は、公開Core APIの別契約です **[環境による]**。専用service JWTと承認範囲が必要で、MCPの接続キーを直接このAPIへ送れません。取込MCPの内部でどの実行主体・経路を使うかは環境管理者へ確認します。8ツールの存在を、134操作すべてのMCP対応とみなしません。[service接続](service-access.md)を参照してください。

## 8ツールの契約

以下は確認した配布クライアントから抽出した定義です。ツール名・入力・annotationsは一致し、説明文のHUB表記だけを基盤に一般化しています。[機械可読JSON](../mcp-tools.json)も配信しています。

```json
{
  "protocol_version": "2025-06-18",
  "adapter": "claudia-customer-imports",
  "adapter_version": "1.0.1",
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
      "description": "指定CSVを検査し差分計画を作る。まだ業務表へ反映しない。ファイルは転送フォルダ内に限定する。大きなファイルは分割して送信し、確認は裏で進む（stateがpreparingのとき）。stateがpreparedになるまでimports_statusで確認してから、imports_runを行う。",
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
      "description": "計画の状態、確認中（preparing）の進み具合、完了区間数を確認する。prepare_failedのときはerror.codeが失敗理由。",
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
      "description": "取込結果を基盤から再取得し全値を照合する。",
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
```

## 出力と状態

APIのJSON結果は`content[0].text`内のJSON文字列です。`isError`と内容を確認します。

| ツール | 出力と注意 |
| --- | --- |
| imports_catalog | 形式、headers、key_columns、format、field_types。datasetは返されたidを使う |
| imports_prepare | 計画id、source_sha256、差分件数、state。preparingではstatusで進捗を確認し、preparedになるまでrunしない |
| imports_status | 準備の進捗・完了区間。prepare_failedのerror.codeも確認 |
| imports_run | 同じplan_id・source_sha256で最大4区間ずつ反映・再開 |
| imports_verify | 全区間完了後の全値照合。成功はverified。不一致はVERIFY_MISMATCH |
| imports_history | 利用者の履歴・再開可能な計画（最新100件まで） |
| imports_cancel | 未実行のpreparedのみ取消。実行後はRESUME_REQUIRED |
| imports_export | 新しいCSVファイルに保存しsaved_fileとbytesを返す。上書きしない |

通信断だけで失敗・未反映と決めません。新しい計画を作らず、同じplan_idとsource_sha256で状態を取得し直します。

## 接続できないとき

1.0.1は、TLS・入口・API・タイムアウトを区別して案内します。生の応答本文や資格をログ・Issueに貼り付けず、公開できるcode、HTTP、日時、クライアント版を記録します。

| 症状 | 対処 |
| --- | --- |
| TLS_CERTIFICATE_VERIFY_FAILED / TLS_CA_UNAVAILABLE | 時刻、配布物のCAバンドル、環境管理者の信頼するCAを確認。SSL_CERT_FILEで明示CAを指定できます。TLS検証は無効にしない |
| ENTRY_REJECTED / HTTP 403、非JSONのerror code: 1010 | 入口の拒否。旧1.0.0から現在の配布物へ更新して確認。1.0.1でも続く場合は管理者に入口の調査を依頼 |
| JSONのAPI拒否（authentication_required等） | 接続先・キーの期限・取消・現在の権限を確認。無効なキーは再発行して同じbaseとcredential-nameで保存 |
| CONNECTION_TIMEOUT / 結果不明 | plan_id・source_sha256を保持してstatusを確認。同じ計画を再開し、二重の計画を作らない |
| キーの保存・読取失敗 | 同じOS利用者、Windows DPAPIまたはLinux Secret Serviceの利用可能性・ロック状態を確認。macOS保存は未提供 |

## 旧1.0.0の記録と1.0.1の確認

2026-10-04の1.0.0では入口403・`error code: 1010`と既定証明書ストアのTLS失敗が記録されていました。1.0.1には製品固有User-Agent、固定CAバンドル、区別したエラー案内が入り、2026-10-08の[公開読取確認報告](https://github.com/mxd2024/claudia-partner-docs/issues/16)では旧入口拒否が解消しています。

この確認は初期化・ツール一覧・取込先一覧・履歴・状態の読取に限ります。書込と全環境は未確認です。製品のUser-Agentは認可の代替ではなく、識別の偽装やTLS無効化で回避しません。[提供状況](versions.md)と[サポート](support.md)を参照してください。
