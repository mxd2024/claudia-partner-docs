# 共通ルール

APIを使うときに、共通して知っておくルールです。用語は、[用語集](https://mxd2024.github.io/claudia-partner-docs/v0.7/glossary.html)を参照してください。

## v1とv2の選び方

系列ごとの、主な対象は次のとおりです。

| 系列 | 主な対象 |
| --- | --- |
| v1 | 顧客が定義する表（`/v1/tables`）、案件（`/v1/jobs`）、請求書、連絡先などの業務API |
| v2 | 業務表（`/v2/tables`）、案件（`/v2/cases`）、行の所有権、関連・所属、アプリの定義、serviceの資格、画像（`/v2/media`） |

v1の表や既存の案件を、URLをv2に変えて移行することはできません。移行には、専用のAPI（`/v2/data-migrations`など）を使います。自動の移行や、同じデータの共有を前提にせず、利用している保存先とアプリの契約を確認してください。

## 検索とページング

v1とv2の通常の検索は、次の項目を使います。

| 項目 | 内容 |
| --- | --- |
| `limit` | 1〜199（既定は50） |
| `sort` | `{field, direction}` |
| `filters` | 最大8個。`op`は`eq`、`contains`、`gte`、`lte` |
| `status` | 状態での絞り込み |
| `cursor` | 続きを取得するための値 |

列が検索できるかどうかは、definitionで確認します。任意のSQL、正規表現、OR式は受け付けません。serviceの検索は別の契約で、`limit`と`after`を使い、通常の検索の`filters`は使えません。

`next_cursor`が`null`になるまで、同じ条件と、返された`cursor`で続けます。`CURSOR_STALE`が返ったら、蓄積したページを捨てて、最初から検索し直します。古いページと新しいページを、画面で混ぜないでください。v2の一覧やごみ箱には、`after` / `next_after`を使うものがあり、画像には`offset`を使うものがあります。各操作のschemaを優先してください。

## 変更の監視とレート

`changes`は、revisionを確認するポーリングです。SSEではありません。関連・所属の変更イベントの取得も、HTTPで`cursor`を送り、メタデータだけのイベント、`has_more`、次の`cursor`を受け取ります。更新された行の内容は、現在の権限で、改めて取得します。

レートの上限は、次のとおりです。

- 表とアプリの操作は、同時に2要求までです。
- serviceは、同時に2要求までと、承認された`rpm`（1〜120）です。
- すべての操作に共通の固定の上限は、定めていません。環境側の制限があり、429が返ることがあります。

429では、`Retry-After`が返れば従います。返らないときは、待つ間隔を延ばして、回数に上限を付けて再試行します。詳しくは、[エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/errors.html)。

## 認可の条件の読み方

OpenAPIの各操作の`x-required-authority`は、次の項目に分かれています。

- 主体（本人またはservice）
- MFAの要否
- 認証の鮮度
- 必要な権限
- 資源ごとの確認

必要な権限が空でも、無権限でよいとは限りません。管理者の権限や、表・行・列の権限は、資源ごとの確認で、別に宣言されます。

`max_authentication_age_seconds`が`null`なのは、その操作に固有の、再認証の時間の上限がないという意味です。トークン、セッション、権限の有効期限を、無視してよいという意味ではありません。画像の操作は、親の資源の読み取りに認可を委ねるため、`binding_rules`で条件が異なります。

## 再送の方式

GET以外であることだけでは、変更の操作とは限りません。検索、集計、計画のPOSTは、読み取りまたは計画の操作です。

| 値 | 使いみち |
| --- | --- |
| `version` / `revision` | 競合の検出 |
| `fingerprint` | 確認した計画との一致の確認 |
| `Idempotency-Key` / `attempt_id` | 受付の識別（二重の実行の防止） |

移行の開始や、旧台帳の採用は、`migration_id`と、元の本文・fingerprintで、既存の結果を確認します。各操作の`x-retry-policy`に、方式、識別子、結果の確認の方法を載せています。次の表は、`Idempotency-Key`を使わない操作と、結果が不明なときの確認の方法です。

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
