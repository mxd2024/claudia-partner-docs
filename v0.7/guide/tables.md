# 表とデータの更新

基盤には、v1の顧客定義の表と、v2の業務表を扱うAPIがあります。パスや版の意味が異なるため、使うAPIの系列を混ぜずに実装します。選び方は、[共通ルール](https://mxd2024.github.io/claudia-partner-docs/v0.7/concepts.html)を参照してください。

## 読み取りから始める

1. 利用できる表の一覧を取得します（次の例はv1）。
2. 表の定義を読みます。表示用のラベルとは別に、安定したfield IDと、型・権限を保持します。
3. 検索条件、sort、cursorを指定して、行を取得します。応答の列は、現在の認可で絞り込まれています。

```http
GET /v1/tables
GET /v1/tables/work_notes
POST /v1/tables/work_notes/query
```

`work_notes`は、説明用の表の名前です。実際に使える表は、対象の環境の一覧で確認します。

## 行を追加・更新する

[実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)に、v1の表一覧・検索・batch、v2の表の定義・作成・更新・削除・復元、関連、`If-Match`の、完全なHTTPの要求と応答を載せています。

書き込みのbatchには、`Authorization`、`Content-Type`、`Idempotency-Key`を付けます。本文には、現在の`schema_version`と、操作ごとの`version`を指定します。

- v1の新しい行のidは、クライアントが作ります。v2では、基盤が作ります。混同しないでください。
- 省略、`null`、空文字は、別の値です。

## 版と再送を管理する

| 値 | 意味 |
| --- | --- |
| `schema_version` | 列・型など、表の定義の版 |
| 行の`version` | その行の更新の競合を確認する版 |
| `If-Match` | 操作の仕様が要求する、期待する版 |
| `Idempotency-Key` | 同じ操作の再送を識別するキー |

更新と削除は、取得した現在の版と、操作の内容を固定して送ります。通信が途切れたときは、結果が不明のことがあります。同じ操作を、別のキーで作り直す前に、状態を確認します。412では、対象を再取得し、差分を利用者に確認してから、次の操作を決めます。詳しくは、[競合・再送・復帰](https://mxd2024.github.io/claudia-partner-docs/v0.7/reliability.html)。

## v2の業務表、関連、ごみ箱

v2では、業務表・案件、関連、transaction、履歴、ごみ箱と復元などの操作を提供します。具体的なパスとschemaは、[APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/api.html)で、「業務表・案件」または「関連・所属」を選んで確認します。通しの手順は、[アプリの登録と運用](https://mxd2024.github.io/claudia-partner-docs/v0.7/tutorial.html)。

削除と、原本の物理的な削除は、同じ意味ではありません。ごみ箱、添付の解除、外部の原本の保持を区別して扱います。

## CSVとAIからの更新

現在の取込MCPは、登録されたデータ形式に対して、CSVの検査、差分の計画、確認後の反映、照合、出力を行います。計画を作っただけでは、業務表へ反映されません。詳しくは、[MCPの導入](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html)。
