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
| 500 / 503 | 基盤側の問題、一時的な停止、結果未確定 | request_idを記録。結果確認前の別操作再送を避ける |
| 507 | 管理容量の上限 | 環境管理者へ容量・保持方針を確認 |

## 通信が途切れた場合

応答が届かなくても、書込み自体は完了していることがあります。同じ操作の識別子・Idempotency-Key・期待版を保存し、計画の状態や最新のデータで結果を確認します。

OUTCOME_UNKNOWNなど結果未確定の応答は、単純な失敗として別の更新を作る根拠にはなりません。認証切れや権限変更がある場合も、再送時の現在権限で評価されます。

## 定義されているエラーコード

以下は、公開OpenAPIのコード表と、操作への対応から生成しています。画像を含む各機能には、個別の条件もあります。対象の操作の応答と、合わせて確認してください。

| HTTP | code | 意味と対応 |
| --- | --- | --- |
| 400 | `ASSET_INVALID` | APIの型・必須項目を確認する |
| 400 | `ASSET_INVALID_IMAGE` | APIの型・必須項目を確認する |
| 400 | `BAD_REQUEST` | APIの型・必須項目を確認する |
| 400 | `ETAG_MALFORMED` | APIの型・必須項目を確認する |
| 400 | `SELF_DECLARED_HEADER` | APIの型・必須項目を確認する |
| 401 | `AUTH_REQUIRED` | 認証を更新する、または再ログインする |
| 401 | `TOKEN_EXPIRED` | トークンの期限が切れています。更新または再ログインする |
| 401 | `TOKEN_INVALID` | トークンが無効です。ログイン直後は反映待ちのことがあります。待機枠で再確認し、続くときは再ログインする |
| 403 | `AI_MUST_USE_PROPOSALS` | 現在の権限とMFAを確認する |
| 403 | `AI_SUSPENDED` | 現在の権限とMFAを確認する |
| 403 | `ASSET_FORBIDDEN` | 現在の権限とMFAを確認する |
| 403 | `ASSET_POLICY_DENIED` | 現在の権限とMFAを確認する |
| 403 | `FIELD_NOT_WRITABLE` | 現在の権限とMFAを確認する |
| 403 | `FORBIDDEN_ROLE` | 現在の権限とMFAを確認する |
| 403 | `MFA_REQUIRED` | 現在の権限とMFAを確認する |
| 403 | `REAUTH_REQUIRED` | 現在の権限とMFAを確認する |
| 403 | `SCOPE_VIOLATION` | 現在の権限とMFAを確認する |
| 404 | `ASSET_NOT_FOUND` | 対象の存在と権限を確認する（隠された対象を推測しない） |
| 404 | `ASSET_NO_THUMBNAIL` | 対象の存在と権限を確認する（隠された対象を推測しない） |
| 404 | `NOT_FOUND` | 対象の存在と権限を確認する（隠された対象を推測しない） |
| 409 | `ASSET_IDEMPOTENCY_MISMATCH` | 同じキーで、本文を変えて送っています。本文を元に戻して再送するか、状態を確認してから、新しいキーで送る |
| 409 | `ASSET_POLICY_CHANGED` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `ASSET_VERSION_CONFLICT` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `AUTHORITY_CONFLICT` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `CURSOR_STALE` | 一覧が変わり、`cursor`が使えません。蓄積したページを捨てて、最初から検索し直す |
| 409 | `DUPLICATE` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `IDEMPOTENCY_IN_PROGRESS` | 同じキーの操作が処理中です。待ってから、同じキーで結果を確認する |
| 409 | `LOCK_BUSY` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `PROPOSAL_CONFLICT` | 状態を再取得し、同じ操作の結果を確認する |
| 409 | `STATE_CONFLICT` | 状態を再取得し、同じ操作の結果を確認する |
| 412 | `VERSION_CONFLICT` | 期待した版と現在の版が一致しません。再取得し、差分を確認してから、操作を決め直す |
| 413 | `ASSET_TOO_LARGE` | 入力やファイルを訂正する |
| 413 | `PAYLOAD_TOO_LARGE` | 入力やファイルを訂正する |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | 入力やファイルを訂正する |
| 422 | `EMPTY_PATCH` | 入力やファイルを訂正する |
| 422 | `FIELD_NOT_ALLOWED` | 入力やファイルを訂正する |
| 422 | `FIELD_REQUIRED` | 入力やファイルを訂正する |
| 422 | `FIELD_UNKNOWN` | 入力やファイルを訂正する |
| 422 | `IDEMPOTENCY_MISMATCH` | 同じキーで、本文を変えて送っています。本文を元に戻して再送するか、状態を確認してから、新しいキーで送る |
| 422 | `INVALID_TRANSITION` | 入力やファイルを訂正する |
| 422 | `VALIDATION_FAILED` | 入力やファイルを訂正する |
| 428 | `ASSET_PRECONDITION_REQUIRED` | 必須の条件（版・理由・再送キー）を付ける |
| 428 | `ASSET_REASON_REQUIRED` | 必須の条件（版・理由・再送キー）を付ける |
| 428 | `IDEMPOTENCY_KEY_REQUIRED` | 必須の条件（版・理由・再送キー）を付ける |
| 428 | `PRECONDITION_REQUIRED` | 必須の条件（版・理由・再送キー）を付ける |
| 429 | `AI_RATE_LIMITED` | `Retry-After`に従い、間隔を空けて再試行する |
| 429 | `RATE_LIMITED` | `Retry-After`に従い、間隔を空けて再試行する |
| 500 | `INTERNAL_CONTRACT_VIOLATION` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `ASSET_BUSY` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `ASSET_CAPACITY` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `ASSET_DEPENDENCY_UNAVAILABLE` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `DEPENDENCY_UNAVAILABLE` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `MAINTENANCE` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `OUTCOME_UNKNOWN` | 操作が完了したか確認できません。同じキーと本文で結果を確認する。別のキーで再実行しない |
| 503 | `TX_ABORT_UNCONFIRMED` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 503 | `TX_RETRY_EXHAUSTED` | `request_id`を記録する。結果を確認する前に、別の操作を再送しない |
| 507 | `ASSET_QUOTA_EXCEEDED` | 環境管理者に、容量と保持の方針を確認する |
