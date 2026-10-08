# 共通ルール

基盤APIを使うときに、どの操作でも共通して守るルールです。APIの系列（v1とv2）の選び方、検索の方法、レートの上限、認可の条件の読み方、再送の方式を説明します。用語は、[用語集](glossary.md)にもあります。

## v1とv2の選び方

基盤APIには、v1とv2の2つの系列があります。パスの先頭が`/v1`か`/v2`かで、見分けられます。系列ごとに、扱える対象が違います。

| 系列 | 主な対象 |
| --- | --- |
| v1 | 顧客が定義する表（`/v1/tables`）、ジョブ（`/v1/jobs`）、請求書、連絡先などの業務API |
| v2 | 業務表（`/v2/tables`）、ケース（`/v2/cases`）、行の所有権、関連・所属、アプリの定義、serviceの資格、画像（`/v2/media`） |

v1の表や既存のジョブを、パスをv2に変えて、そのまま使うことはできません。移行には、専用のAPI（`/v2/data-migrations`など）を使います。データが自動で移行される、または同じデータを共有できる、とは考えないでください。利用している保存先と、アプリの契約を確認してください。

## 検索とページング

表の行を検索するとき、v1とv2の通常の検索は、次の項目を使います。

| 項目 | 内容 |
| --- | --- |
| `limit` | 1回に取得する件数。1〜199（既定は50） |
| `sort` | 並べ替え。`{field, direction}` |
| `filters` | 絞り込み。最大8個。`op`は`eq`、`contains`、`gte`、`lte` |
| `status` | 状態での絞り込み |
| `cursor` | 続きを取得するための値 |

列が検索できるかどうかは、definition（表の定義）で確認します。任意のSQL、正規表現、OR式は、受け付けません。serviceの検索は、別の契約で、`limit`と`after`を使います。通常の検索の`filters`は、使えません。

続きがあるときは、応答の`next_cursor`が入っています。`next_cursor`が`null`になるまで、同じ条件と、返された`cursor`で、取得を続けます。

`CURSOR_STALE`が返ったら、それまでに集めたページを捨てて、最初から検索し直します。古いページと新しいページを、同じ画面で混ぜないでください。v2の一覧やごみ箱には、`after`と`next_after`を使うものがあります。画像には、`offset`を使うものがあります。各操作のschemaを優先してください。

## 変更の監視とレート

変更の監視（`changes`）は、一定の間隔で、更新の有無を問い合わせる方式です。サーバーから通知が届く方式（SSE）では、ありません。関連・所属の変更イベントの取得も、HTTPで`cursor`を送り、メタデータだけのイベント、`has_more`、次の`cursor`を受け取ります。更新された行の内容は、現在の権限で、改めて取得します。

要求の頻度には、次の制限があります。

- 表とアプリの操作は、同時に2要求までです。
- serviceは、同時に2要求までと、承認された`rpm`（1分あたりの上限。1〜120）です。
- すべての操作に共通の、固定の上限は、定めていません。環境側の制限があり、429が返ることがあります。

429が返ったときは、`Retry-After`があれば、その時間だけ待ちます。なければ、待つ間隔を延ばし、回数の上限を決めて、再試行します。詳しくは、[エラーと再試行](errors.md)にあります。

## 認可の条件の読み方

OpenAPIの各操作には、`x-required-authority`があり、その操作を実行できる条件が書かれています。次の項目に分かれています。

- 主体（利用者またはservice）
- MFAが必要か
- 認証の鮮度（どれだけ最近、認証したか）
- 必要な権限
- 資源ごとの確認（表、列、行など）

必要な権限が空のときも、誰でも実行できる、という意味ではありません。管理者の権限や、表・行・列の権限は、資源ごとの確認の項目に、別に書かれています。

`max_authentication_age_seconds`が`null`のときは、その操作に固有の、再認証の時間の上限がない、という意味です。トークン、セッション、権限の有効期限を、無視してよいという意味ではありません。画像の操作は、親の資源の読み取りの権限に、判断を任せます。そのため、`binding_rules`で、条件が異なります。

## 再送の方式

通信が途切れたときに、同じ操作をもう一度送ってよいかは、操作によって違います。GET以外のメソッドでも、変更の操作とは限りません。検索、集計、計画のPOSTは、読み取りまたは計画の操作です。

| 値 | 使いみち |
| --- | --- |
| `version` / `revision` | 競合の検出 |
| `fingerprint` | 確認した計画と、一致しているかの確認 |
| `Idempotency-Key` / `attempt_id` | 同じ操作の再送の識別（二重の実行の防止） |

再送のキー（`Idempotency-Key`）の保持期間は、定めていません。保証として扱わないでください。キーが紐づく範囲は、APIごとに違います。ヘッダーの定義と、各操作の`x-retry-policy`に従います。service申請の`Idempotency-Key`は、UUIDが必須で、申請そのものの識別子になります。他のAPIの、8〜128文字のキーは、応答を再生するためのキーで、同じ意味ではありません。版（`version`）だけで、競合を検査する管理操作もあります。結果が不明なときは、同じキー、同じ本文、同じ前提を保持して、再送します。版だけを更新して、再送しないでください。新しい論理の操作には、新しいキーを使います。

移行の開始や、旧台帳の採用は、`migration_id`と、元の本文・`fingerprint`で、既存の結果を確認します。各操作の`x-retry-policy`に、方式、識別子、結果の確認の方法があります。次の表は、`Idempotency-Key`以外の方式で再送を管理する操作（`workspace.import`を含む）と、結果が不明なときの確認の方法です。

| 操作 | 種別 | 方式 | 結果不明時の確認 |
| --- | --- | --- | --- |
| table.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| table.export | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.import | write | Idempotency-Key | 同じキー・本文・前提版で再送し受領結果を確認する。現在権限も再検査する。競合時は最新状態と利用者の意図を照合し、版だけを置換しない。 |
| workspace.export | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.exportRecords | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.aggregate | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.caseQuery | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspace.socket.events | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| asset.check | verification | none | GET /v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId} で状態を確認。専用の再送識別子・応答再生保証なし。 |
| service.permissions | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。 |
| service.delete | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。 |
| service.grantPut | write | version | GET /v2/access/grants/{subjectId}/{collection} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。 |
| service.change | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。 |
| service.activate | write | none | GET /v2/service-clients/{clientId}（人の管理権限で照合） で状態を確認。専用の再送識別子・応答再生保証なし。 |
| service.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| workspaceAccess.subjects | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| app-packages.migrationPreview | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| app-packages.migrationPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| app-packages.migrationBegin | write | fingerprint | 同じ主体・移行ID・本文・fingerprintで再送すると既存jobを返す。GET /v2/data-migrations/{migrationId} でも状態を確認。変更した入力やfingerprintでは再送しない。 |
| app-packages.migrationCancel | write | version | GET /v2/data-migrations/{migrationId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。 |
| app-packages.adoptionPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| app-packages.requirementsPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| app-packages.plan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| organization.settingsPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| organization.activity | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| apps.plan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。 |
| identity.logoutSelf | write | attempt_id | 同じセッションとattempt_idで再送し失効受領を確認する。別attempt_idを自動発行しない。 |
