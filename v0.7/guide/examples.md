# HTTP・Python・JavaScript実行例

以下は合成データの完全な要求・応答例です。HTTPヘッダーとJSONは[共通examples JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/public-requests.json)から生成し、OpenAPIのexamplesにも同じ内容を使用します。時刻、UUID、版、fingerprint、storeは説明用です。実行時には現在の取得結果へ置き換えてください。

成功応答の値は固定の期待値ではありません。表の権限や現在版に従い変化します。公開資料は検証用のデータ投入を自動的に行いません。[通し手順](https://mxd2024.github.io/claudia-partner-docs/v0.7/tutorial.html)に沿い、検証専用の表で実行してください。

## サンプルの実行

[Python](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/request.py)はPython 3.10以上の標準ライブラリ、[JavaScript](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples/request.mjs)はNode.js 22以上で動作します。どちらも選択した1要求のみを送信し、自動再試行しません。examples JSONを同じフォルダーへ保存して、置換済みの要求ファイルを指定します。

```sh
python request.py --base https://api.example.invalid --request my-request.json
node request.mjs --base https://api.example.invalid --request my-request.json
```

資格は環境変数CP_ACCESS_TOKEN、またはPythonの非表示対話入力で渡します。スクリプトや要求ファイルへ埋め込みません。CP_ACCESS_TOKENは[認証手順](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html)で取得したaccess_tokenです。baseは管理者交付のCore HTTPS originへ置き換えます。検証CAはPythonの --ca 引数、NodeのNODE_EXTRA_CA_CERTSで設定し、TLS検証を無効化しません。

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

## If-Matchで既存案件を更新

```json
{
  "id": "if-match",
  "title": "If-Matchで既存案件を更新",
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
