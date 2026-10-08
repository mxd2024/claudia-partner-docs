# HTTP・実行例

60の例（56操作）を載せています。すべて合成データの要求と応答です。HTTPヘッダーとJSONは[共通examples JSON](../examples/public-requests.json)から生成し、OpenAPIのexamplesにも同じ内容を使用します。時刻、UUID、版、fingerprint、storeは説明用です。実行時には現在の取得結果へ置き換えてください。

成功応答の値は固定の期待値ではありません。表の権限や現在版に従い変化します。公開資料は検証用のデータ投入を自動的に行いません。[アプリの登録と運用](tutorial.md)に沿い、検証専用の表で実行してください。

## サンプルの実行

[Python](../examples/request.py)はPython 3.10以上の標準ライブラリ、[JavaScript](../examples/request.mjs)はNode.js 22以上で動作します。どちらも選択した1要求のみを送信し、自動再試行しません。examples JSONを同じフォルダーへ保存して、置換済みの要求ファイルを指定します。

```sh
python request.py --base https://api.example.invalid --request my-request.json
node request.mjs --base https://api.example.invalid --request my-request.json
```

資格は環境変数CP_ACCESS_TOKEN、またはPythonの非表示対話入力で渡します。スクリプトや要求ファイルへ埋め込みません。CP_ACCESS_TOKENは[利用者として接続する](authentication.md)で取得したaccess_tokenです。baseは、環境管理者から受け取った、基盤のHTTPS originへ置き換えます。検証CAはPythonの --ca 引数、NodeのNODE_EXTRA_CA_CERTSで設定し、TLS検証を無効化しません。

my-request.jsonは下の共通JSONから1件を選び、headers内のAuthorizationプレースホルダー以外の値、url、bodyを実環境向けに直したものです。書込はIdempotency-Keyと期待版を確認してから実行します。

## 本人を確認

```json
{
  "id": "me",
  "title": "本人を確認",
  "method": "GET",
  "path": "/v1/me",
  "url": "/v1/me",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response": {
    "id": "11111111-1111-4111-8111-111111111111",
    "actor_type": "human",
    "permissions": [],
    "capabilities": [],
    "contract_expires_at": null,
    "checked_at": "2026-10-04T00:00:00Z",
    "session": {
      "absolute_expires_at": "2026-10-04T01:00:00Z",
      "idle_expires_at": "2026-10-04T00:30:00Z"
    }
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v1の表一覧

```json
{
  "id": "tables",
  "title": "v1の表一覧",
  "method": "GET",
  "path": "/v1/tables",
  "url": "/v1/tables",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response": {
    "items": [
      {
        "id": "demo_tasks",
        "revision": 1,
        "label": "作業"
      }
    ],
    "role": "designer"
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v1の最初のページ

```json
{
  "id": "v1-query",
  "title": "v1の最初のページ",
  "method": "POST",
  "path": "/v1/tables/{collection}/query",
  "url": "/v1/tables/demo_tasks/query",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "limit": 50,
    "sort": {
      "field": "title",
      "direction": "asc"
    },
    "filters": [
      {
        "field": "title",
        "op": "contains",
        "value": "見本"
      }
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "items": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "status": "committed",
        "values": {
          "title": "見本"
        }
      }
    ],
    "next_cursor": null,
    "revision": 2,
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v1行を作成

```json
{
  "id": "v1-batch",
  "title": "v1行を作成",
  "method": "POST",
  "path": "/v1/tables/{collection}/batch",
  "url": "/v1/tables/demo_tasks/batch",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-v1-create-001"
  },
  "body": {
    "schema_version": 1,
    "operations": [
      {
        "action": "create",
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 0,
        "status": "committed",
        "values": {
          "title": "見本"
        }
      }
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "rows": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "deleted": false
      }
    ],
    "schema_version": 1,
    "revision": 2,
    "committed": true
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v2表を定義

```json
{
  "id": "v2-define",
  "title": "v2表を定義",
  "method": "PUT",
  "path": "/v2/tables/{collection}",
  "url": "/v2/tables/demo_tasks",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "If-Match": "\"0\"",
    "Idempotency-Key": "docs-v2-define-001"
  },
  "body": {
    "label": "作業",
    "fields": [
      {
        "id": "title",
        "label": "件名",
        "type": "text",
        "required": true,
        "read": [
          "staff"
        ],
        "write": [
          "staff"
        ],
        "searchable": true,
        "choices": []
      }
    ],
    "export_roles": [
      "staff"
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v2行を作成

```json
{
  "id": "v2-create",
  "title": "v2行を作成",
  "method": "POST",
  "path": "/v2/tables/{collection}/batch",
  "url": "/v2/tables/demo_tasks/batch",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-v2-create-001"
  },
  "body": {
    "schema_version": 1,
    "operations": [
      {
        "action": "create",
        "status": "committed",
        "values": {
          "title": "見本"
        }
      }
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "rows": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "deleted": false
      }
    ],
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v2行を検索

```json
{
  "id": "v2-query",
  "title": "v2行を検索",
  "method": "POST",
  "path": "/v2/tables/{collection}/query",
  "url": "/v2/tables/demo_tasks/query",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "limit": 50
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "items": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "status": "committed",
        "values": {
          "title": "見本"
        },
        "closed": false,
        "is_owner": true
      }
    ],
    "next_cursor": null,
    "revision": "sample-visible-revision",
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v2行を更新

```json
{
  "id": "v2-update",
  "title": "v2行を更新",
  "method": "POST",
  "path": "/v2/tables/{collection}/batch",
  "url": "/v2/tables/demo_tasks/batch",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-v2-update-001"
  },
  "body": {
    "schema_version": 1,
    "operations": [
      {
        "action": "update",
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "values": {
          "title": "確認済み"
        }
      }
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "rows": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 2,
        "deleted": false
      }
    ],
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## v2行をごみ箱へ

```json
{
  "id": "v2-delete",
  "title": "v2行をごみ箱へ",
  "method": "POST",
  "path": "/v2/tables/{collection}/batch",
  "url": "/v2/tables/demo_tasks/batch",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-v2-delete-001"
  },
  "body": {
    "schema_version": 1,
    "operations": [
      {
        "action": "delete",
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 2,
        "reason": "検証用の行を削除"
      }
    ]
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "rows": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 3,
        "deleted": true
      }
    ],
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 行をごみ箱から復元

```json
{
  "id": "v2-restore",
  "title": "行をごみ箱から復元",
  "method": "POST",
  "path": "/v2/tables/{collection}/trash/{trashId}/restore",
  "url": "/v2/tables/demo_tasks/trash/22222222-2222-4222-8222-222222222222/restore",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-v2-restore-001"
  },
  "body": {
    "version": 3,
    "reason": "検証後に復元"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "id": "11111111-1111-4111-8111-111111111111",
    "version": 4,
    "trash_id": "22222222-2222-4222-8222-222222222222",
    "schema_version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 子表の親所属を設定

```json
{
  "id": "relation",
  "title": "子表の親所属を設定",
  "method": "PUT",
  "path": "/v2/tables/{collection}/access",
  "url": "/v2/tables/demo_lines/access",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "If-Match": "\"0\"",
    "Idempotency-Key": "docs-relation-001"
  },
  "body": {
    "mode": "members",
    "parent_collection": "demo_tasks",
    "field": "parent_id",
    "cardinality": "many"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "version": 1
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 本人へ表利用権を設定

```json
{
  "id": "grant",
  "title": "本人へ表利用権を設定",
  "method": "PUT",
  "path": "/v2/access/grants/{subjectId}/{collection}",
  "url": "/v2/access/grants/11111111-1111-4111-8111-111111111111/demo_tasks",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "version": 0,
    "enabled": true,
    "role": "staff",
    "read_scope": "all",
    "write_scope": "all",
    "can_design": true,
    "can_close": true,
    "can_import": true,
    "expires_at": "2026-10-05T00:00:00Z"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "version": 1,
    "grant": {
      "actor": "11111111-1111-4111-8111-111111111111",
      "client": "hub-spa",
      "collection": "demo_tasks",
      "role": "staff",
      "read_scope": "all",
      "write_scope": "all",
      "can_design": true,
      "can_close": true,
      "can_import": true,
      "expires_at": "2026-10-05T00:00:00Z"
    }
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## アプリ登録計画

```json
{
  "id": "app-plan",
  "title": "アプリ登録計画",
  "method": "POST",
  "path": "/v2/apps/plan",
  "url": "/v2/apps/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "id": "demo_app",
    "version": 1,
    "name": "検証アプリ",
    "datasets": [
      {
        "id": "demo_tasks",
        "mode": "owned",
        "definition": {
          "label": "作業",
          "fields": [
            {
              "id": "title",
              "label": "件名",
              "type": "text",
              "required": true,
              "read": [
                "staff"
              ],
              "write": [
                "staff"
              ],
              "searchable": true,
              "choices": []
            }
          ],
          "export_roles": [
            "staff"
          ]
        }
      }
    ],
    "dependencies": []
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "revision": 0,
    "changes": [
      {
        "id": "demo_tasks",
        "mode": "owned",
        "action": "create",
        "version": 0
      }
    ]
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 確認したアプリ計画を反映

```json
{
  "id": "app-apply",
  "title": "確認したアプリ計画を反映",
  "method": "POST",
  "path": "/v2/apps/apply",
  "url": "/v2/apps/apply",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-app-apply-001"
  },
  "body": {
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "id": "demo_app",
    "version": 1,
    "revision": 1,
    "state": "active",
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "deleted_at": null,
    "restore_until": null
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## アプリを停止

```json
{
  "id": "app-stop",
  "title": "アプリを停止",
  "method": "POST",
  "path": "/v2/apps/{appId}/state",
  "url": "/v2/apps/demo_app/state",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Idempotency-Key": "docs-app-stop-001"
  },
  "body": {
    "action": "stop",
    "revision": 1,
    "reason": "検証停止"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "id": "demo_app",
    "version": 1,
    "revision": 2,
    "state": "stopped",
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "deleted_at": null,
    "restore_until": null
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## serviceの許可済み表を取得

```json
{
  "id": "service-query",
  "title": "serviceの許可済み表を取得",
  "method": "POST",
  "path": "/v2/service/tables/{collection}/query",
  "url": "/v2/service/tables/demo_tasks/query",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "limit": 50
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "schema_version": 1,
    "items": [
      {
        "id": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "values": {
          "title": "見本"
        },
        "status": "committed",
        "closed": false
      }
    ],
    "next_after": null
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 外部原本への画像参照

```json
{
  "id": "media-reference",
  "title": "外部原本への画像参照",
  "method": "POST",
  "path": "/v2/media/{collection}/{rowId}/{field}/{assetId}/reference",
  "url": "/v2/media/demo_tasks/11111111-1111-4111-8111-111111111111/picture/22222222-2222-4222-8222-222222222222/reference",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "If-Match": "\"0\"",
    "Idempotency-Key": "docs-media-ref-001",
    "X-Parent-Version": "1",
    "X-Schema-Version": "1"
  },
  "body": {
    "store": "demo-store",
    "relative_path": "examples/sample.png",
    "media_type": "image/png",
    "name": "見本.png"
  },
  "content_type": "application/json",
  "status": 200,
  "response": {
    "asset_id": "22222222-2222-4222-8222-222222222222",
    "version": 1,
    "deleted": false,
    "updated_at": "2026-10-04T00:00:00Z",
    "custody": "external_reference",
    "media_type": "image/png",
    "name": "見本.png",
    "size": 70,
    "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "preview": "ready"
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## If-Matchで既存ケースを更新

```json
{
  "id": "if-match",
  "title": "If-Matchで既存ケースを更新",
  "method": "PATCH",
  "path": "/v1/jobs/{id}",
  "url": "/v1/jobs/11111111-1111-4111-8111-111111111111",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/merge-patch+json",
    "If-Match": "\"1\"",
    "Idempotency-Key": "docs-job-patch-001"
  },
  "body": {
    "notes": "確認済み"
  },
  "content_type": "application/merge-patch+json",
  "status": 200,
  "response": {
    "id": "11111111-1111-4111-8111-111111111111",
    "version": "2"
  },
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 古い版で更新すると412

```json
{
  "id": "conflict",
  "title": "古い版で更新すると412",
  "method": "PATCH",
  "path": "/v1/jobs/{id}",
  "url": "/v1/jobs/11111111-1111-4111-8111-111111111111",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/merge-patch+json",
    "If-Match": "\"1\"",
    "Idempotency-Key": "docs-job-patch-002"
  },
  "body": {
    "notes": "別の変更"
  },
  "content_type": "application/merge-patch+json",
  "status": 412,
  "response": {
    "type": "urn:hub:problem:version-conflict",
    "title": "操作を完了できません",
    "status": 412,
    "code": "VERSION_CONFLICT",
    "request_id": "33333333-3333-4333-8333-333333333333"
  },
  "response_type": "application/problem+json",
  "response_headers": {
    "Content-Type": "application/problem+json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## 資格なしは401

```json
{
  "id": "auth-required",
  "title": "資格なしは401",
  "method": "GET",
  "path": "/v1/me",
  "url": "/v1/me",
  "headers": {
    "Accept": "application/json"
  },
  "status": 401,
  "response": {
    "type": "urn:hub:problem:auth-required",
    "title": "操作を完了できません",
    "status": 401,
    "code": "AUTH_REQUIRED",
    "request_id": "33333333-3333-4333-8333-333333333333"
  },
  "response_type": "application/problem+json",
  "response_headers": {
    "Content-Type": "application/problem+json",
    "X-Request-Id": "33333333-3333-4333-8333-333333333333",
    "Cache-Control": "no-store"
  }
}
```

## データ移行の一覧を取得

```json
{
  "id": "app-packages-migrationList",
  "title": "データ移行の一覧を取得",
  "method": "GET",
  "path": "/v2/data-migrations",
  "url": "/v2/data-migrations",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "items": [
      {
        "id": "44444444-4444-4444-8444-444444444444",
        "app": "demo_app",
        "state": "scanning",
        "revision": 1,
        "created_at": "2026-10-04T00:00:00Z",
        "is_owner": true
      }
    ]
  }
}
```

## 移行前後の行を比較

```json
{
  "id": "app-packages-migrationPreview",
  "title": "移行前後の行を比較",
  "method": "POST",
  "path": "/v2/data-migrations/{migrationId}/preview",
  "url": "/v2/data-migrations/44444444-4444-4444-8444-444444444444/preview",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "collection": "demo_tasks"
  },
  "content_type": "application/json",
  "response": {
    "collection": "demo_tasks",
    "items": [
      {
        "id": "22222222-2222-4222-8222-222222222222",
        "before": {
          "title": "合成データ"
        },
        "after_values": {
          "title": "合成データ"
        },
        "error": null
      }
    ]
  }
}
```

## データ移行計画を作成

```json
{
  "id": "app-packages-migrationPlan",
  "title": "データ移行計画を作成",
  "method": "POST",
  "path": "/v2/data-migrations/plan",
  "url": "/v2/data-migrations/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "migration_id": "44444444-4444-4444-8444-444444444444",
    "package": {
      "manifest": {
        "id": "demo_app",
        "version": 1,
        "name": "検証アプリ",
        "datasets": [
          {
            "id": "demo_tasks",
            "mode": "owned",
            "definition": {
              "label": "作業",
              "fields": [
                {
                  "id": "title",
                  "label": "件名",
                  "type": "text",
                  "required": true,
                  "read": [
                    "staff"
                  ],
                  "write": [
                    "staff"
                  ],
                  "searchable": true,
                  "choices": []
                }
              ],
              "export_roles": [
                "staff"
              ]
            }
          }
        ],
        "dependencies": []
      },
      "csv": [
        {
          "collection": "demo_tasks",
          "key_fields": [
            "title"
          ]
        }
      ]
    },
    "transforms": [
      {
        "collection": "demo_tasks",
        "fields": [
          {
            "target": "title",
            "source": "title",
            "convert": "identity"
          }
        ]
      }
    ],
    "reason": "列定義の移行を検証"
  },
  "content_type": "application/json",
  "response": {
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "migration": {
      "migration_id": "44444444-4444-4444-8444-444444444444",
      "package": {
        "manifest": {
          "id": "demo_app",
          "version": 1,
          "name": "検証アプリ",
          "datasets": [
            {
              "id": "demo_tasks",
              "mode": "owned",
              "definition": {
                "label": "作業",
                "fields": [
                  {
                    "id": "title",
                    "label": "件名",
                    "type": "text",
                    "required": true,
                    "read": [
                      "staff"
                    ],
                    "write": [
                      "staff"
                    ],
                    "searchable": true,
                    "choices": []
                  }
                ],
                "export_roles": [
                  "staff"
                ]
              }
            }
          ],
          "dependencies": []
        },
        "csv": [
          {
            "collection": "demo_tasks",
            "key_fields": [
              "title"
            ]
          }
        ]
      },
      "transforms": [
        {
          "collection": "demo_tasks",
          "fields": [
            {
              "target": "title",
              "source": "title",
              "convert": "identity"
            }
          ]
        }
      ],
      "reason": "列定義の移行を検証"
    },
    "tables": [
      {
        "collection": "demo_tasks",
        "version": 1,
        "count": 1
      }
    ]
  }
}
```

## 確認済みデータ移行を開始

```json
{
  "id": "app-packages-migrationBegin",
  "title": "確認済みデータ移行を開始",
  "method": "POST",
  "path": "/v2/data-migrations/begin",
  "url": "/v2/data-migrations/begin",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "migration": {
      "migration_id": "44444444-4444-4444-8444-444444444444",
      "package": {
        "manifest": {
          "id": "demo_app",
          "version": 1,
          "name": "検証アプリ",
          "datasets": [
            {
              "id": "demo_tasks",
              "mode": "owned",
              "definition": {
                "label": "作業",
                "fields": [
                  {
                    "id": "title",
                    "label": "件名",
                    "type": "text",
                    "required": true,
                    "read": [
                      "staff"
                    ],
                    "write": [
                      "staff"
                    ],
                    "searchable": true,
                    "choices": []
                  }
                ],
                "export_roles": [
                  "staff"
                ]
              }
            }
          ],
          "dependencies": []
        },
        "csv": [
          {
            "collection": "demo_tasks",
            "key_fields": [
              "title"
            ]
          }
        ]
      },
      "transforms": [
        {
          "collection": "demo_tasks",
          "fields": [
            {
              "target": "title",
              "source": "title",
              "convert": "identity"
            }
          ]
        }
      ],
      "reason": "列定義の移行を検証"
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "response": {
    "id": "44444444-4444-4444-8444-444444444444",
    "state": "scanning",
    "revision": 1,
    "app": "demo_app",
    "reason": "列定義の移行を検証",
    "targets": [
      {
        "collection": "demo_tasks",
        "source_count": 1,
        "scanned": 0,
        "cursor": null,
        "done": false
      }
    ],
    "verified": 0,
    "errors": [],
    "error_count": 0,
    "response": null
  }
}
```

## データ移行の進捗を取得

```json
{
  "id": "app-packages-migrationGet",
  "title": "データ移行の進捗を取得",
  "method": "GET",
  "path": "/v2/data-migrations/{migrationId}",
  "url": "/v2/data-migrations/44444444-4444-4444-8444-444444444444",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "id": "44444444-4444-4444-8444-444444444444",
    "state": "scanning",
    "revision": 1,
    "app": "demo_app",
    "reason": "列定義の移行を検証",
    "targets": [
      {
        "collection": "demo_tasks",
        "source_count": 1,
        "scanned": 0,
        "cursor": null,
        "done": false
      }
    ],
    "verified": 0,
    "errors": [],
    "error_count": 0,
    "response": null
  }
}
```

## データ移行を次の区間へ進める

```json
{
  "id": "app-packages-migrationNext",
  "title": "データ移行を次の区間へ進める",
  "method": "POST",
  "path": "/v2/data-migrations/{migrationId}/next",
  "url": "/v2/data-migrations/44444444-4444-4444-8444-444444444444/next",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "revision": 1
  },
  "content_type": "application/json",
  "response": {
    "id": "44444444-4444-4444-8444-444444444444",
    "state": "verifying",
    "revision": 2,
    "app": "demo_app",
    "reason": "列定義の移行を検証",
    "targets": [
      {
        "collection": "demo_tasks",
        "source_count": 1,
        "scanned": 1,
        "cursor": "22222222-2222-4222-8222-222222222222",
        "done": true
      }
    ],
    "verified": 0,
    "errors": [],
    "error_count": 0,
    "response": null
  }
}
```

## 検証済みデータ移行を確定

```json
{
  "id": "app-packages-migrationCommit",
  "title": "検証済みデータ移行を確定",
  "method": "POST",
  "path": "/v2/data-migrations/{migrationId}/commit",
  "url": "/v2/data-migrations/44444444-4444-4444-8444-444444444444/commit",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "revision": 3
  },
  "content_type": "application/json",
  "response": {
    "id": "44444444-4444-4444-8444-444444444444",
    "state": "committed",
    "revision": 4,
    "app": "demo_app",
    "reason": "列定義の移行を検証",
    "targets": [
      {
        "collection": "demo_tasks",
        "source_count": 1,
        "scanned": 1,
        "cursor": "22222222-2222-4222-8222-222222222222",
        "done": true
      }
    ],
    "verified": 1,
    "errors": [],
    "error_count": 0,
    "response": {
      "id": "demo_app"
    }
  }
}
```

## データ移行を中止

```json
{
  "id": "app-packages-migrationCancel",
  "title": "データ移行を中止",
  "method": "POST",
  "path": "/v2/data-migrations/{migrationId}/cancel",
  "url": "/v2/data-migrations/44444444-4444-4444-8444-444444444444/cancel",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "revision": 1,
    "reason": "移行計画を見直す"
  },
  "content_type": "application/json",
  "response": {
    "id": "44444444-4444-4444-8444-444444444444",
    "state": "cancelled",
    "revision": 2
  }
}
```

## 既存アプリ台帳の採用を計画

```json
{
  "id": "app-packages-adoptionPlan",
  "title": "既存アプリ台帳の採用を計画",
  "method": "POST",
  "path": "/v2/app-adoptions/plan",
  "url": "/v2/app-adoptions/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "migration_id": "44444444-4444-4444-8444-444444444444",
    "source_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "apps": [
      {
        "package": {
          "manifest": {
            "id": "demo_app",
            "version": 1,
            "name": "検証アプリ",
            "datasets": [
              {
                "id": "demo_tasks",
                "mode": "owned",
                "definition": {
                  "label": "作業",
                  "fields": [
                    {
                      "id": "title",
                      "label": "件名",
                      "type": "text",
                      "required": true,
                      "read": [
                        "staff"
                      ],
                      "write": [
                        "staff"
                      ],
                      "searchable": true,
                      "choices": []
                    }
                  ],
                  "export_roles": [
                    "staff"
                  ]
                }
              }
            ],
            "dependencies": []
          },
          "csv": [
            {
              "collection": "demo_tasks",
              "key_fields": [
                "title"
              ]
            }
          ],
          "requirements": {
            "dependencies": [],
            "integrations": [],
            "service_clients": []
          }
        },
        "revision": 1,
        "state": "active",
        "legacy_state": "registered"
      }
    ]
  },
  "content_type": "application/json",
  "response": {
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "migration_id": "44444444-4444-4444-8444-444444444444",
    "source_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "observed": {}
  }
}
```

## 確認済みの既存アプリ台帳を採用

```json
{
  "id": "app-packages-adoptionApply",
  "title": "確認済みの既存アプリ台帳を採用",
  "method": "POST",
  "path": "/v2/app-adoptions/apply",
  "url": "/v2/app-adoptions/apply",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "migration": {
      "migration_id": "44444444-4444-4444-8444-444444444444",
      "source_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "apps": [
        {
          "package": {
            "manifest": {
              "id": "demo_app",
              "version": 1,
              "name": "検証アプリ",
              "datasets": [
                {
                  "id": "demo_tasks",
                  "mode": "owned",
                  "definition": {
                    "label": "作業",
                    "fields": [
                      {
                        "id": "title",
                        "label": "件名",
                        "type": "text",
                        "required": true,
                        "read": [
                          "staff"
                        ],
                        "write": [
                          "staff"
                        ],
                        "searchable": true,
                        "choices": []
                      }
                    ],
                    "export_roles": [
                      "staff"
                    ]
                  }
                }
              ],
              "dependencies": []
            },
            "csv": [
              {
                "collection": "demo_tasks",
                "key_fields": [
                  "title"
                ]
              }
            ],
            "requirements": {
              "dependencies": [],
              "integrations": [],
              "service_clients": []
            }
          },
          "revision": 1,
          "state": "active",
          "legacy_state": "registered"
        }
      ]
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "response": {
    "migration_id": "44444444-4444-4444-8444-444444444444",
    "source_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "states": {
      "demo_app": "active"
    },
    "apps": [
      {
        "id": "demo_app",
        "version": 1,
        "revision": 1,
        "state": "active",
        "manifest": {
          "id": "demo_app",
          "version": 1,
          "name": "検証アプリ",
          "datasets": [
            {
              "id": "demo_tasks",
              "mode": "owned",
              "definition": {
                "label": "作業",
                "fields": [
                  {
                    "id": "title",
                    "label": "件名",
                    "type": "text",
                    "required": true,
                    "read": [
                      "staff"
                    ],
                    "write": [
                      "staff"
                    ],
                    "searchable": true,
                    "choices": []
                  }
                ],
                "export_roles": [
                  "staff"
                ]
              }
            }
          ],
          "dependencies": []
        },
        "deleted_at": null,
        "restore_until": null
      }
    ]
  }
}
```

## アプリ接続要件の変更を計画

```json
{
  "id": "app-packages-requirementsPlan",
  "title": "アプリ接続要件の変更を計画",
  "method": "POST",
  "path": "/v2/apps/{appId}/requirements/plan",
  "url": "/v2/apps/demo_app/requirements/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "dependencies": [],
    "integrations": [],
    "service_clients": []
  },
  "content_type": "application/json",
  "response": {
    "revision": 1,
    "before": {
      "dependencies": [],
      "integrations": [],
      "service_clients": []
    },
    "requirements": {
      "dependencies": [],
      "integrations": [],
      "service_clients": []
    },
    "blockers": [],
    "dependencies": [],
    "clients": [],
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "app_revision": 1,
    "state_after": "active"
  }
}
```

## 確認済みアプリ接続要件を適用

```json
{
  "id": "app-packages-requirementsApply",
  "title": "確認済みアプリ接続要件を適用",
  "method": "POST",
  "path": "/v2/apps/{appId}/requirements/apply",
  "url": "/v2/apps/demo_app/requirements/apply",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "requirements": {
      "dependencies": [],
      "integrations": [],
      "service_clients": []
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "response": {
    "id": "demo_app",
    "version": 1,
    "revision": 1,
    "state": "active",
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "deleted_at": null,
    "restore_until": null,
    "requirements": {
      "revision": 1,
      "before": {
        "dependencies": [],
        "integrations": [],
        "service_clients": []
      },
      "requirements": {
        "dependencies": [],
        "integrations": [],
        "service_clients": []
      },
      "blockers": [],
      "dependencies": [],
      "clients": []
    }
  }
}
```

## 本人が利用可能な取込形式を一覧取得

```json
{
  "id": "app-packages-profiles",
  "title": "本人が利用可能な取込形式を一覧取得",
  "method": "GET",
  "path": "/v2/import-profiles",
  "url": "/v2/import-profiles",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "items": [
      {
        "contract_id": "44444444-4444-4444-8444-444444444444",
        "kind": "workspace-v1",
        "id": "demo_tasks",
        "collection": "demo_tasks",
        "label": "作業",
        "definition": {
          "label": "作業",
          "fields": [
            {
              "id": "title",
              "label": "件名",
              "type": "text",
              "required": true,
              "read": [
                "staff"
              ],
              "write": [
                "staff"
              ],
              "searchable": true,
              "choices": []
            }
          ],
          "export_roles": [
            "staff"
          ]
        },
        "key_columns": [
          "title"
        ],
        "headers": [
          "title"
        ]
      }
    ]
  }
}
```

## 版付きCSV契約で行を取込

```json
{
  "id": "app-packages-import",
  "title": "版付きCSV契約で行を取込",
  "method": "POST",
  "path": "/v2/tables/{collection}/import-profile",
  "url": "/v2/tables/demo_tasks/import-profile",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "contract_id": "44444444-4444-4444-8444-444444444444",
    "schema_version": 1,
    "expected_actor": "11111111-1111-4111-8111-111111111111",
    "operations": [
      {
        "action": "create",
        "values": {
          "title": "合成データ"
        },
        "status": "committed"
      }
    ]
  },
  "content_type": "application/json",
  "response": {
    "rows": [
      {
        "id": "22222222-2222-4222-8222-222222222222",
        "version": 1,
        "deleted": false
      }
    ],
    "schema_version": 1
  }
}
```

## アプリとCSV契約を取得

```json
{
  "id": "app-packages-get",
  "title": "アプリとCSV契約を取得",
  "method": "GET",
  "path": "/v2/app-packages/{appId}",
  "url": "/v2/app-packages/demo_app",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "id": "demo_app",
    "version": 1,
    "revision": 1,
    "state": "active",
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "deleted_at": null,
    "restore_until": null,
    "csv": [
      {
        "collection": "demo_tasks",
        "key_fields": [
          "title"
        ]
      }
    ]
  }
}
```

## アプリとCSV契約の変更を計画

```json
{
  "id": "app-packages-plan",
  "title": "アプリとCSV契約の変更を計画",
  "method": "POST",
  "path": "/v2/app-packages/plan",
  "url": "/v2/app-packages/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "csv": [
      {
        "collection": "demo_tasks",
        "key_fields": [
          "title"
        ]
      }
    ]
  },
  "content_type": "application/json",
  "response": {
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "app_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "revision": 0,
    "changes": [
      {
        "id": "demo_tasks",
        "mode": "owned",
        "action": "create",
        "version": 0
      }
    ],
    "csv_before": [],
    "csv_after": [
      {
        "collection": "demo_tasks",
        "key_fields": [
          "title"
        ]
      }
    ]
  }
}
```

## 確認済みアプリとCSV契約を適用

```json
{
  "id": "app-packages-apply",
  "title": "確認済みアプリとCSV契約を適用",
  "method": "POST",
  "path": "/v2/app-packages/apply",
  "url": "/v2/app-packages/apply",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "package": {
      "manifest": {
        "id": "demo_app",
        "version": 1,
        "name": "検証アプリ",
        "datasets": [
          {
            "id": "demo_tasks",
            "mode": "owned",
            "definition": {
              "label": "作業",
              "fields": [
                {
                  "id": "title",
                  "label": "件名",
                  "type": "text",
                  "required": true,
                  "read": [
                    "staff"
                  ],
                  "write": [
                    "staff"
                  ],
                  "searchable": true,
                  "choices": []
                }
              ],
              "export_roles": [
                "staff"
              ]
            }
          }
        ],
        "dependencies": []
      },
      "csv": [
        {
          "collection": "demo_tasks",
          "key_fields": [
            "title"
          ]
        }
      ]
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "response": {
    "id": "demo_app",
    "version": 1,
    "revision": 1,
    "state": "active",
    "manifest": {
      "id": "demo_app",
      "version": 1,
      "name": "検証アプリ",
      "datasets": [
        {
          "id": "demo_tasks",
          "mode": "owned",
          "definition": {
            "label": "作業",
            "fields": [
              {
                "id": "title",
                "label": "件名",
                "type": "text",
                "required": true,
                "read": [
                  "staff"
                ],
                "write": [
                  "staff"
                ],
                "searchable": true,
                "choices": []
              }
            ],
            "export_roles": [
              "staff"
            ]
          }
        }
      ],
      "dependencies": []
    },
    "deleted_at": null,
    "restore_until": null,
    "csv": [
      {
        "collection": "demo_tasks",
        "key_fields": [
          "title"
        ]
      }
    ]
  }
}
```

## 専用環境の容量とアプリ件数を取得

```json
{
  "id": "organization-overview",
  "title": "専用環境の容量とアプリ件数を取得",
  "method": "GET",
  "path": "/v2/organization/overview",
  "url": "/v2/organization/overview",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "as_of": "2026-10-04T00:00:00Z",
    "data_api": "available",
    "applications": {
      "active": 1,
      "stopped": 0,
      "detached": 0,
      "trashed": 0
    },
    "defined_tables": 1,
    "storage": {
      "database_bytes": 10485760,
      "quota_bytes": null,
      "managed_object_bytes": null,
      "external_original_bytes": null,
      "backup_bytes": null
    },
    "measurement_scope": "dedicated_environment_database",
    "backup_state": "not_connected",
    "contract_state": "not_connected"
  }
}
```

## 組織設定を取得

```json
{
  "id": "organization-settings",
  "title": "組織設定を取得",
  "method": "GET",
  "path": "/v2/organization/settings",
  "url": "/v2/organization/settings",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "version": 1,
    "values": {
      "organization_name": "検証用組織",
      "contact_note": "連絡先は別途交付"
    },
    "updated_at": "2026-10-04T00:00:00Z"
  }
}
```

## 組織設定の変更を計画

```json
{
  "id": "organization-settingsPlan",
  "title": "組織設定の変更を計画",
  "method": "POST",
  "path": "/v2/organization/settings/plan",
  "url": "/v2/organization/settings/plan",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "version": 1,
    "values": {
      "organization_name": "検証用組織",
      "contact_note": "連絡先は別途交付"
    },
    "reason": "表示名を更新"
  },
  "content_type": "application/json",
  "response": {
    "before": {
      "version": 1,
      "values": {
        "organization_name": "検証用組織",
        "contact_note": "連絡先は別途交付"
      },
      "updated_at": "2026-10-04T00:00:00Z"
    },
    "change": {
      "version": 1,
      "values": {
        "organization_name": "検証用組織",
        "contact_note": "連絡先は別途交付"
      },
      "reason": "表示名を更新"
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  }
}
```

## 確認済み組織設定を適用

```json
{
  "id": "organization-settingsApply",
  "title": "確認済み組織設定を適用",
  "method": "POST",
  "path": "/v2/organization/settings/apply",
  "url": "/v2/organization/settings/apply",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "change": {
      "version": 1,
      "values": {
        "organization_name": "検証用組織",
        "contact_note": "連絡先は別途交付"
      },
      "reason": "表示名を更新"
    },
    "fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "content_type": "application/json",
  "response": {
    "version": 2,
    "values": {
      "organization_name": "検証用組織",
      "contact_note": "連絡先は別途交付"
    },
    "updated_at": "2026-10-04T00:00:00Z"
  }
}
```

## 確定操作の履歴を検索

```json
{
  "id": "organization-activity",
  "title": "確定操作の履歴を検索",
  "method": "POST",
  "path": "/v2/organization/activity",
  "url": "/v2/organization/activity",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "limit": 20,
    "source": "organization"
  },
  "content_type": "application/json",
  "response": {
    "items": [
      {
        "source": "organization",
        "sequence": "1",
        "request_id": "44444444-4444-4444-8444-444444444444",
        "actor": "11111111-1111-4111-8111-111111111111",
        "client": "hub-spa",
        "target": "organization",
        "action": "settings.apply",
        "reason": "表示名を更新",
        "at": "2026-10-04T00:00:00Z"
      }
    ],
    "next_cursor": null,
    "until": "2026-10-04T00:01:00Z",
    "sources": [
      "organization"
    ]
  }
}
```

## 本人の行削除範囲を取得

```json
{
  "id": "workspaceAccess-deleteGet",
  "title": "本人の行削除範囲を取得",
  "method": "GET",
  "path": "/v2/access/deletions/{subjectId}/{collection}",
  "url": "/v2/access/deletions/11111111-1111-4111-8111-111111111111/demo_people",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "version": 0,
    "grant": null
  }
}
```

## 本人の行削除範囲を設定

```json
{
  "id": "workspaceAccess-deletePut",
  "title": "本人の行削除範囲を設定",
  "method": "PUT",
  "path": "/v2/access/deletions/{subjectId}/{collection}",
  "url": "/v2/access/deletions/11111111-1111-4111-8111-111111111111/demo_people",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "version": 0,
    "scope": "own",
    "expires_at": "2026-10-05T00:00:00Z",
    "reason": "本人の行の削除を許可"
  },
  "content_type": "application/json",
  "response": {
    "version": 1,
    "grant": {
      "version": 1,
      "scope": "own",
      "expires_at": "2026-10-05T00:00:00Z",
      "source": "explicit"
    }
  }
}
```

## 人物表の登録状態を取得

```json
{
  "id": "workspaceAccess-rootGet",
  "title": "人物表の登録状態を取得",
  "method": "GET",
  "path": "/v2/access/people/{collection}",
  "url": "/v2/access/people/demo_people",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "version": 0,
    "root": null
  }
}
```

## 人物表を登録

```json
{
  "id": "workspaceAccess-rootPut",
  "title": "人物表を登録",
  "method": "PUT",
  "path": "/v2/access/people/{collection}",
  "url": "/v2/access/people/demo_people",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "version": 0,
    "enabled": true,
    "reason": "人物表として登録"
  },
  "content_type": "application/json",
  "response": {
    "version": 1,
    "root": {
      "collection": "demo_people",
      "version": 1,
      "enabled": true
    }
  }
}
```

## 本人IDと人物行の対応を取得

```json
{
  "id": "workspaceAccess-bindingGet",
  "title": "本人IDと人物行の対応を取得",
  "method": "GET",
  "path": "/v2/access/people/{collection}/bindings/{subjectId}",
  "url": "/v2/access/people/demo_people/bindings/11111111-1111-4111-8111-111111111111",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "version": 0,
    "binding": null
  }
}
```

## 本人IDと人物行の対応を設定

```json
{
  "id": "workspaceAccess-bindingPut",
  "title": "本人IDと人物行の対応を設定",
  "method": "PUT",
  "path": "/v2/access/people/{collection}/bindings/{subjectId}",
  "url": "/v2/access/people/demo_people/bindings/11111111-1111-4111-8111-111111111111",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "version": 0,
    "person_id": "22222222-2222-4222-8222-222222222222",
    "enabled": true,
    "expires_at": "2026-10-05T00:00:00Z",
    "reason": "検証用本人を人物行に対応付け"
  },
  "content_type": "application/json",
  "response": {
    "version": 1,
    "binding": {
      "person_id": "22222222-2222-4222-8222-222222222222",
      "version": 1,
      "enabled": true,
      "expires_at": "2026-10-05T00:00:00Z"
    }
  }
}
```

## 人物行の所属者を取得

```json
{
  "id": "workspaceAccess-membersGet",
  "title": "人物行の所属者を取得",
  "method": "GET",
  "path": "/v2/access/people/{collection}/rows/{personId}/members",
  "url": "/v2/access/people/demo_people/rows/22222222-2222-4222-8222-222222222222/members",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "items": [
      {
        "actor": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "enabled": true,
        "write": false,
        "expires_at": "2026-10-05T00:00:00Z"
      }
    ],
    "next_after": null
  }
}
```

## 人物行の所属者を設定

```json
{
  "id": "workspaceAccess-membersPut",
  "title": "人物行の所属者を設定",
  "method": "PUT",
  "path": "/v2/access/people/{collection}/rows/{personId}/members",
  "url": "/v2/access/people/demo_people/rows/22222222-2222-4222-8222-222222222222/members",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "reason": "閲覧所属を登録",
    "members": [
      {
        "actor": "11111111-1111-4111-8111-111111111111",
        "version": 0,
        "enabled": true,
        "write": false,
        "expires_at": "2026-10-05T00:00:00Z"
      }
    ]
  },
  "content_type": "application/json",
  "response": {
    "items": [
      {
        "actor": "11111111-1111-4111-8111-111111111111",
        "version": 1,
        "enabled": true,
        "write": false,
        "expires_at": "2026-10-05T00:00:00Z"
      }
    ]
  }
}
```

## 本人に対応する人物行を取得

```json
{
  "id": "workspaceAccess-me",
  "title": "本人に対応する人物行を取得",
  "method": "GET",
  "path": "/v2/people/{collection}/me",
  "url": "/v2/people/demo_people/me",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "resolution": "resolved",
    "person_id": "22222222-2222-4222-8222-222222222222",
    "binding_version": 1
  }
}
```

## 行に対応する本人IDを検索

```json
{
  "id": "workspaceAccess-subjects",
  "title": "行に対応する本人IDを検索",
  "method": "POST",
  "path": "/v2/tables/{collection}/subjects/query",
  "url": "/v2/tables/demo_people/subjects/query",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "rows": [
      {
        "id": "22222222-2222-4222-8222-222222222222",
        "version": 1
      }
    ]
  },
  "content_type": "application/json",
  "response": {
    "person_collection": "demo_people",
    "items": [
      {
        "row_id": "22222222-2222-4222-8222-222222222222",
        "row_version": 1,
        "person_id": "22222222-2222-4222-8222-222222222222"
      }
    ]
  }
}
```

## 資産の保存・参照方針を取得

```json
{
  "id": "asset-policy",
  "title": "資産の保存・参照方針を取得",
  "method": "GET",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/policy",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/policy",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "contract_version": 1,
    "modes": [
      "managed_original",
      "external_reference"
    ],
    "max_managed_bytes": 8388608,
    "max_external_bytes": 33554432,
    "media_types": [
      "application/pdf",
      "image/png"
    ],
    "can_write": true
  }
}
```

## 資産の一覧取得

```json
{
  "id": "asset-list",
  "title": "資産の一覧取得",
  "method": "GET",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "items": [
      {
        "asset_id": "55555555-5555-4555-8555-555555555555",
        "version": 1,
        "custody": "external_reference",
        "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "size": 1024,
        "media_type": "application/pdf",
        "thumbnail": false,
        "created_at": "2026-10-04T00:00:00Z"
      }
    ],
    "limit": 25,
    "offset": 0
  }
}
```

## 資産のメタデータを取得

```json
{
  "id": "asset-get",
  "title": "資産のメタデータを取得",
  "method": "GET",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "asset_id": "55555555-5555-4555-8555-555555555555",
    "version": 1,
    "custody": "external_reference",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "size": 1024,
    "media_type": "application/pdf",
    "thumbnail": false,
    "created_at": "2026-10-04T00:00:00Z"
  }
}
```

## 資産の原本を取得

```json
{
  "id": "asset-content",
  "title": "資産の原本を取得",
  "method": "GET",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}/content",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555/content",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/octet-stream",
  "response_headers": {
    "Content-Type": "application/octet-stream",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store",
    "ETag": "\"1\""
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。 この資産は1px PNGのmanaged_original。バイナリーをbase64で表記。",
  "response_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg=="
}
```

## 資産の原本を保存

```json
{
  "id": "asset-upload",
  "title": "資産の原本を保存",
  "method": "PUT",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}/content",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555/content",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "If-Match": "\"0\"",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/octet-stream",
    "X-Asset-Media-Type": "image/png"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg==",
  "content_type": "application/octet-stream",
  "response": {
    "asset_id": "55555555-5555-4555-8555-555555555555",
    "version": 1,
    "custody": "managed_original",
    "sha256": "abc58d5127d7cdf313beb9ec8ee839860a9c6bfbc48c8b8eb6a3f7d8bb63de6f",
    "size": 70,
    "media_type": "image/png",
    "thumbnail": true,
    "created_at": "2026-10-04T00:00:00Z"
  }
}
```

## 資産のサムネイルを取得

```json
{
  "id": "asset-thumbnail",
  "title": "資産のサムネイルを取得",
  "method": "GET",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}/thumbnail",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555/thumbnail",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "image/png",
  "response_headers": {
    "Content-Type": "image/png",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store",
    "ETag": "\"1\""
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。 この資産は1px PNGのmanaged_original。バイナリーをbase64で表記。",
  "response_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg=="
}
```

## 資産の外部原本への参照を登録

```json
{
  "id": "asset-reference",
  "title": "資産の外部原本への参照を登録",
  "method": "POST",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}/reference",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555/reference",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json",
    "If-Match": "\"0\"",
    "Idempotency-Key": "demo-request-20261004-01",
    "Content-Type": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "body": {
    "relative_path": "demo/reference.pdf",
    "media_type": "application/pdf"
  },
  "content_type": "application/json",
  "response": {
    "asset_id": "55555555-5555-4555-8555-555555555555",
    "version": 1,
    "custody": "external_reference",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "size": 1024,
    "media_type": "application/pdf",
    "thumbnail": false,
    "created_at": "2026-10-04T00:00:00Z"
  }
}
```

## 資産の外部原本の現在状態を照合

```json
{
  "id": "asset-check",
  "title": "資産の外部原本の現在状態を照合",
  "method": "POST",
  "path": "/v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId}/check",
  "url": "/v1/assets/jobs/job/22222222-2222-4222-8222-222222222222/55555555-5555-4555-8555-555555555555/check",
  "headers": {
    "Authorization": "Bearer <ACCESS_TOKEN>",
    "Accept": "application/json"
  },
  "status": 200,
  "response_type": "application/json",
  "response_headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "44444444-4444-4444-8444-444444444444",
    "Cache-Control": "no-store"
  },
  "notes": "合成例。各例は独立した前提状態。実API実行結果ではない。ID・版・期限を実値へ置換し、fingerprintは対応するplan応答をそのまま使う。",
  "response": {
    "asset_id": "55555555-5555-4555-8555-555555555555",
    "version": 1,
    "status": "available",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  }
}
```

バイナリー例はbody_base64/response_base64で実バイトを表します。実行サンプルは送信時にdecodeし、バイナリー応答はbase64で表示します。JSON文字列を画像として送る形式ではありません。
