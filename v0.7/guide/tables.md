# 表・データ更新

Claudia Partnerには、v1の顧客定義表と、v2の業務表・案件を扱うAPIがあります。パスや版の意味が異なるため、利用するAPI系列を混ぜずに実装します。

## 読取りから始める

1. 利用可能な表の一覧を取得します。以下はv1の例です。
2. 表定義を読み、表示用ラベルとは別に、安定したfield IDと型・権限を保持します。
3. 検索条件・sort・cursorを指定して行を取得します。応答の列は現在の認可で投影されます。

```http
GET /v1/tables
GET /v1/tables/work_notes
POST /v1/tables/work_notes/query
```

上記のwork_notesは説明用の表名です。実際に使える表は対象環境の一覧で確認します。

## 要求・応答の例

[共通実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)に、v1の表一覧・query・batch、v2の表定義・CRUD・復元、関連、If-Matchの完全なHTTP要求と応答を掲載しています。OpenAPIと同じJSONを使用します。

書込みbatchには Authorization、Content-Type、Idempotency-Keyを付けます。本文には現在のschema_versionと操作ごとのversionを指定します。v1の新規行idはクライアントで生成、v2の新規行idはCoreが生成するため混同しません。省略値、null、空文字は別の値です。

## 版と再送を管理する

| 値 | 意味 |
| --- | --- |
| schema_version | 列・型など表定義の版 |
| 行のversion | その行の更新競合を確認する版 |
| If-Match | 対象操作の仕様が要求する期待版 |
| Idempotency-Key | 同じ操作の再送を識別するキー |

更新・削除は、取得した現在版と操作の内容を固定して送ります。通信が途切れたときは結果が未確定の可能性があります。同じ操作を別キーで作り直す前に、状態や受領票を確認します。412では対象を再取得し、差分を利用者に確認してから次の操作を決めます。

## v2の業務表、関連、ごみ箱

v2では業務表・案件、関連、transaction、履歴、ごみ箱・復元などの操作を提供します。具体的なパスとschemaは[APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/api.html)で「業務表・案件」または「関連・ソケット」を選択してください。

削除と原本の物理削除は同じ意味ではありません。ごみ箱、添付の解除、外部原本の保持を区別して扱います。

## CSVとAIからの更新

現行の取込MCPは、登録されたデータ形式に対してCSV検査、差分計画、確認後の反映、照合、出力を行います。計画の作成だけで業務表へ反映されるわけではありません。詳細は[MCPの取込フロー](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html)を参照してください。
