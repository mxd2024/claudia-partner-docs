# エラーと再試行

HTTP statusだけで原因を決めず、応答のcodeとrequest_idを確認します。問い合わせでは操作・時刻・対象環境・request_idを伝え、資格や原票本文は貼り付けません。

## 状況別の対応

| HTTP | 状況の例 | クライアントの対応 |
| --- | --- | --- |
| 400 | 入力形式、ヘッダー、要求の不備 | APIの型・必須項目を確認 |
| 401 | 認証なし、期限切れ、無効な資格 | 認証更新または再ログイン |
| 403 | 現在権限やMFAなどの条件が不足 | codeに応じた権限確認・追加認証 |
| 404 | 不存在、または存在を公開できない対象 | 隠された対象を推測せず画面を更新 |
| 409 | 状態競合、原本の変更、処理中など | 状態を再取得し、同じ操作の結果を確認 |
| 412 | 期待版と現在版の不一致 | 再取得し、差分確認後に操作を決め直す |
| 413 / 415 / 422 | 容量、媒体、値の検証で拒否 | 入力やファイルを訂正 |
| 428 | 期待版・理由・再送キーなどが不足 | 対象操作の必須条件を確認 |
| 429 | レート上限 | Retry-Afterがあれば従い、間隔を空ける |
| 500 / 503 | 内部契約違反、依存停止、結果未確定 | request_idを記録。結果確認前の別操作再送を避ける |
| 507 | 管理容量の上限 | 環境管理者へ容量・保持方針を確認 |

## 通信が途切れた場合

応答が届かなくても、書込み自体は完了していることがあります。同じ操作の識別子・Idempotency-Key・期待版を保存し、受領票、計画状態、最新データで結果を確認します。

OUTCOME_UNKNOWNなど結果未確定の応答は、単純な失敗として別の更新を作る根拠にはなりません。認証切れや権限変更がある場合も、再送時の現在権限で評価されます。

## 定義されているエラーコード

以下は公開OpenAPIのコード表と操作への対応付けから生成しています。「その他」は未使用という断定ではありません。STALE_SOURCEは内部同期契約で使われ、現公開操作との対応はありません。DUPLICATE、EMPTY_PATCH、INVALID_TRANSITION、IDEMPOTENCY_IN_PROGRESSは実装に使用箇所があり、該当する公開操作へ補いました。メディアを含む各機能には個別の条件もあるため、対象操作の応答と合わせて確認してください。

{
  "ASSET_REASON_REQUIRED": {
    "http": 428,
    "usage": "documented_operation_response"
  },
  "ASSET_INVALID": {
    "http": 400,
    "usage": "documented_operation_response"
  },
  "ASSET_INVALID_IMAGE": {
    "http": 400,
    "usage": "documented_operation_response"
  },
  "ASSET_FORBIDDEN": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "ASSET_POLICY_DENIED": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "ASSET_NOT_FOUND": {
    "http": 404,
    "usage": "documented_operation_response"
  },
  "ASSET_NO_THUMBNAIL": {
    "http": 404,
    "usage": "documented_operation_response"
  },
  "ASSET_VERSION_CONFLICT": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "ASSET_IDEMPOTENCY_MISMATCH": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "ASSET_POLICY_CHANGED": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "ASSET_PRECONDITION_REQUIRED": {
    "http": 428,
    "usage": "documented_operation_response"
  },
  "ASSET_TOO_LARGE": {
    "http": 413,
    "usage": "documented_operation_response"
  },
  "ASSET_QUOTA_EXCEEDED": {
    "http": 507,
    "usage": "documented_operation_response"
  },
  "ASSET_DEPENDENCY_UNAVAILABLE": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "ASSET_BUSY": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "ASSET_CAPACITY": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "BAD_REQUEST": {
    "http": 400,
    "usage": "documented_operation_response"
  },
  "ETAG_MALFORMED": {
    "http": 400,
    "usage": "documented_operation_response"
  },
  "SELF_DECLARED_HEADER": {
    "http": 400,
    "usage": "documented_operation_response"
  },
  "AUTH_REQUIRED": {
    "http": 401,
    "usage": "documented_operation_response"
  },
  "TOKEN_INVALID": {
    "http": 401,
    "usage": "documented_operation_response"
  },
  "TOKEN_EXPIRED": {
    "http": 401,
    "usage": "documented_operation_response"
  },
  "FORBIDDEN_ROLE": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "FIELD_NOT_WRITABLE": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "SCOPE_VIOLATION": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "MFA_REQUIRED": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "REAUTH_REQUIRED": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "AI_MUST_USE_PROPOSALS": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "AI_SUSPENDED": {
    "http": 403,
    "usage": "documented_operation_response"
  },
  "NOT_FOUND": {
    "http": 404,
    "usage": "documented_operation_response"
  },
  "STATE_CONFLICT": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "PROPOSAL_CONFLICT": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "DUPLICATE": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "STALE_SOURCE": {
    "http": 409,
    "usage": "other_core_contract_not_mapped_to_public_operation"
  },
  "AUTHORITY_CONFLICT": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "IDEMPOTENCY_IN_PROGRESS": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "LOCK_BUSY": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "CURSOR_STALE": {
    "http": 409,
    "usage": "documented_operation_response"
  },
  "VERSION_CONFLICT": {
    "http": 412,
    "usage": "documented_operation_response"
  },
  "PAYLOAD_TOO_LARGE": {
    "http": 413,
    "usage": "documented_operation_response"
  },
  "UNSUPPORTED_MEDIA_TYPE": {
    "http": 415,
    "usage": "documented_operation_response"
  },
  "FIELD_UNKNOWN": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "FIELD_NOT_ALLOWED": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "FIELD_REQUIRED": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "EMPTY_PATCH": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "VALIDATION_FAILED": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "INVALID_TRANSITION": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "IDEMPOTENCY_MISMATCH": {
    "http": 422,
    "usage": "documented_operation_response"
  },
  "PRECONDITION_REQUIRED": {
    "http": 428,
    "usage": "documented_operation_response"
  },
  "IDEMPOTENCY_KEY_REQUIRED": {
    "http": 428,
    "usage": "documented_operation_response"
  },
  "RATE_LIMITED": {
    "http": 429,
    "usage": "documented_operation_response"
  },
  "AI_RATE_LIMITED": {
    "http": 429,
    "usage": "documented_operation_response"
  },
  "DEPENDENCY_UNAVAILABLE": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "MAINTENANCE": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "OUTCOME_UNKNOWN": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "TX_ABORT_UNCONFIRMED": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "TX_RETRY_EXHAUSTED": {
    "http": 503,
    "usage": "documented_operation_response"
  },
  "INTERNAL_CONTRACT_VIOLATION": {
    "http": 500,
    "usage": "documented_operation_response"
  }
}
