# MCPの対応範囲とトラブル対応

## 対応範囲

現在のMCPで利用できるのは、取込用の8ツールです [提供中]。全APIサービスへの対応は [準備中] です。

DBへの直接の接続、任意のSQL、署名鍵は、MCPの対象に含めません。現在の8ツールの動作を、全APIの提供として扱わないでください。導入の手順は、[MCPの導入](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/mcp.md)。

## 8ツールの契約

```json
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
      "description": "取込結果を基盤から再取得し、全値を照合する。",
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

## 接続できないとき

クライアントが「Connection interrupted」とだけ表示する場合、原因は、HTTPのステータス、content-type、本文で見分けます。次の原因が確認されています。どの場合も、TLS検証の無効化、認証ヘッダーの手動での付与、クライアントの識別の偽装は行いません。

### 接続の前にTLS検証が失敗する（例: certificate has expired）

- 原因: OSの証明書ストアに、期限切れのルート証明書が残る環境で、Pythonの既定の検証が失敗します。
- 対処: 信頼するルート証明書のPEMファイルを、環境変数`SSL_CERT_FILE`に指定して、MCPホストからクライアントを起動します。検証自体は、有効のままにします。

### HTTP 403、content-typeが`text/plain`、本文が`error code: 1010`

- 原因: 管理サイトに届く前の入口で、要求が拒否されています。管理サイトの応答（JSONの`error`）ではありません。
- 対処: 時刻と、本文の`error code: 1010`を添えて、[サポートと窓口](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/support.md)へ連絡します。現在の配布物は、この拒否を受けることがあります。改善した版を提供したときに、版ごとの違いを、ここへ追記します。

### HTTP 401、JSONの`error`が`authentication_required`

- 原因: キーが無効、または失効している。あるいは、別の接続先で発行したキーを使っています。
- 対処: 管理サイトで接続キーを再発行し、同じ`--base`と`--credential-name`で、再保存します。新しいキーでも続くときは、サービス側の設定が原因の可能性があります。[サポートと窓口](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/support.md)へ連絡します。

JSONの`error`が返るときは、アプリまで届いています。`text/plain`の本文だけが返るときは、入口で拒否されています。この違いが、連絡するときの、最初の手がかりになります。

### キーの保存や読み取りが失敗する

実行しているユーザーと、Secret Serviceのロックを確認します。本人用のアクセストークンを、取込のキーの代わりに保存しないでください。
