# MCPの対応範囲とトラブル対応

## 対応範囲

文書対象のMCPは、クライアント1.0.1の取込用8ツールです {{環境による}}。全APIサービスへの対応は {{準備中}} です。

DBへの直接の接続、任意のSQL、署名鍵は、MCPの対象に含めません。現在の8ツールの動作を、全APIの提供として扱わないでください。導入の手順は、[MCPの導入](mcp.html)。

## 8ツールの契約

<!-- generated:mcp-tools -->

## ツールの出力と状態

ツールは、APIのJSONの結果を、MCPの`content[0].text`に、JSONの文字列として返します。

| ツール | 出力と扱い |
| --- | --- |
| `imports_catalog` | 取込の形式の配列。`id`を、`dataset`に使います。`headers`、`key_columns`、`format`、`field_types`で、形式を確認します |
| `imports_prepare` | 計画。`id`、`dataset`、`source_rows`、`created`・`updated`・`unchanged`の件数、`absent_retained`、`source_sha256`、`encoding`、`state`など。`imports_run`などの`plan_id`には、この`id`を渡します。差分を示して、反映してよいか確認します |
| `imports_run` | 同じ`plan_id`と`source_sha256`で、最大4区間ずつ進めます。最後の区間の後は、自動で照合します |
| `imports_status` | 計画の状態と、完了した区間の数を、取得し直します |
| `imports_verify` | 全区間が完了した計画を、インフラの値と照合します。成功は`state=verified`です。未完了は`PLAN_INCOMPLETE`、不一致は`VERIFY_MISMATCH`です |
| `imports_history` | 利用者の計画の配列（最新100件まで） |
| `imports_cancel` | `prepared`の計画だけを、`cancelled`にします。実行した後は、取り消せず、`RESUME_REQUIRED`になります |
| `imports_export` | 新しいファイルに保存して、`saved_file`と`bytes`を返します。既存のファイルは、上書きしません |

準備中は`preparing`、準備完了は`prepared`、準備失敗は`prepare_failed`です。`prepared`を確認してから実行します。実行後は、通常、`running`、`verified`の順に進みます。実行の失敗は`failed`、実行前の取り消しは`cancelled`です。通信が切れただけで、失敗や未反映と決めず、`imports_status`で確認します。同じ計画と、同じ受領のキーを保持して、新しい計画を作って、二重に反映しないでください。

## 接続できないとき

クライアントが「Connection interrupted」とだけ表示する場合、原因は、HTTPのステータス、content-type、本文で見分けます。次の原因が確認されています。どの場合も、TLS検証の無効化、認証ヘッダーの手動での付与、クライアントの識別の偽装は行いません。

### 接続の前にTLS検証が失敗する（例: certificate has expired）

- 確認: システム時計、接続先、信頼するCAと配布物の版を確認します。エラーだけで特定の証明書を原因と断定しません。
- 対処: 1.0.1の同梱CAを使用します。利用環境で別の信頼CAが必要なら、確認済みPEMを`SSL_CERT_FILE`に指定します。指定値は同梱CAより優先されます。TLS検証は有効のままにします。

### HTTP 403、content-typeが`text/plain`、本文が`error code: 1010`

- 原因: 管理サイトに届く前の入口で、要求が拒否されています。管理サイトの応答（JSONの`error`）ではありません。
- 対処: 現行の配布物を確認し、利用環境のサービス管理者へ時刻とエラーコードを伝えます。1.0.1にはこの拒否を`ENTRY_REJECTED`として識別する処理があります。2026-10-08の限定した公開読取検証は成功していますが、すべての環境で入口の拒否が解消したとは限りません。クライアントの識別を偽装したり、TLS検証を無効にしたりして回避しないでください。

### HTTP 401、JSONの`error`が`authentication_required`

- 原因: キーが無効、または失効している。あるいは、別の接続先で発行したキーを使っています。
- 対処: 管理サイトで接続キーを再発行し、同じ`--base`と`--credential-name`で、再保存します。新しいキーでも続くときは、サービス側の設定が原因の可能性があります。[サポートと窓口](support.html)へ連絡します。

JSONの`error`が返るときは、アプリまで届いています。`text/plain`の本文だけが返るときは、入口で拒否されています。この違いが、連絡するときの、最初の手がかりになります。

### キーの保存や読み取りが失敗する

実行しているユーザーと、Secret Serviceのロックを確認します。利用者用のアクセストークンを、取込のキーの代わりに保存しないでください。
