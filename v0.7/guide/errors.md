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

以下は公開OpenAPIのコード表から生成しています。メディアを含む各機能には個別の条件もあるため、対象操作の応答と合わせて確認してください。

{
  "ASSET_REASON_REQUIRED": 428,
  "ASSET_INVALID": 400,
  "ASSET_INVALID_IMAGE": 400,
  "ASSET_FORBIDDEN": 403,
  "ASSET_POLICY_DENIED": 403,
  "ASSET_NOT_FOUND": 404,
  "ASSET_NO_THUMBNAIL": 404,
  "ASSET_VERSION_CONFLICT": 409,
  "ASSET_IDEMPOTENCY_MISMATCH": 409,
  "ASSET_POLICY_CHANGED": 409,
  "ASSET_PRECONDITION_REQUIRED": 428,
  "ASSET_TOO_LARGE": 413,
  "ASSET_QUOTA_EXCEEDED": 507,
  "ASSET_DEPENDENCY_UNAVAILABLE": 503,
  "ASSET_BUSY": 503,
  "ASSET_CAPACITY": 503,
  "BAD_REQUEST": 400,
  "ETAG_MALFORMED": 400,
  "SELF_DECLARED_HEADER": 400,
  "AUTH_REQUIRED": 401,
  "TOKEN_INVALID": 401,
  "TOKEN_EXPIRED": 401,
  "FORBIDDEN_ROLE": 403,
  "FIELD_NOT_WRITABLE": 403,
  "SCOPE_VIOLATION": 403,
  "MFA_REQUIRED": 403,
  "REAUTH_REQUIRED": 403,
  "AI_MUST_USE_PROPOSALS": 403,
  "AI_SUSPENDED": 403,
  "NOT_FOUND": 404,
  "STATE_CONFLICT": 409,
  "PROPOSAL_CONFLICT": 409,
  "DUPLICATE": 409,
  "STALE_SOURCE": 409,
  "AUTHORITY_CONFLICT": 409,
  "IDEMPOTENCY_IN_PROGRESS": 409,
  "LOCK_BUSY": 409,
  "CURSOR_STALE": 409,
  "VERSION_CONFLICT": 412,
  "PAYLOAD_TOO_LARGE": 413,
  "UNSUPPORTED_MEDIA_TYPE": 415,
  "FIELD_UNKNOWN": 422,
  "FIELD_NOT_ALLOWED": 422,
  "FIELD_REQUIRED": 422,
  "EMPTY_PATCH": 422,
  "VALIDATION_FAILED": 422,
  "INVALID_TRANSITION": 422,
  "IDEMPOTENCY_MISMATCH": 422,
  "PRECONDITION_REQUIRED": 428,
  "IDEMPOTENCY_KEY_REQUIRED": 428,
  "RATE_LIMITED": 429,
  "AI_RATE_LIMITED": 429,
  "DEPENDENCY_UNAVAILABLE": 503,
  "MAINTENANCE": 503,
  "OUTCOME_UNKNOWN": 503,
  "TX_ABORT_UNCONFIRMED": 503,
  "TX_RETRY_EXHAUSTED": 503,
  "INTERNAL_CONTRACT_VIOLATION": 500
}
