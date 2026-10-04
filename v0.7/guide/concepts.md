# 概念とAPIの選び方

## v1とv2

v1には既存の案件等の業務APIと顧客定義表があります。v2は業務表、行所有権、関連・所属、アプリ定義、サービス資格などを追加する契約です。v1の表や既存案件は、URLをv2に変えて移行できません。自動移行・同一データの共有を前提にせず、利用中の保存先とアプリ契約を確認します。

## 用語

| 用語 | 意味 |
| --- | --- |
| actor | 認証資格からCoreが解決する内部主体。本人IDを入力して成り代わる仕組みではない |
| human | 本人セッションを持つ人。現在権限と必要なMFAを検査 |
| service | 承認された機械実行主体。表・列・行・CRUD・期限・鍵を限定 |
| collection | 表の識別子。表示ラベルとは別 |
| definition / schema_version | 列と型の定義 / その版。行のversionとは別 |
| version | 行・資格・資産など、取得した資源そのものの版 |
| revision | アプリ状態や一覧等の変更版。対象ごとに意味・型が異なる |
| proposal | 既存業務の承認提案。現契約には取得APIがある。汎用の全操作承認箱ではない |
| plan | 適用前に生成する差分・確認対象。fingerprint等を適用時に照合 |
| manifest | アプリの宣言、または配布物の一覧。文脈を確認 |
| app | 表・依存先・版を登録したアプリ単位。画面プログラムの自動配備とは別 |
| custody | managed_originalは管理された原本、external_referenceは外部原本への参照 |
| draft / committed | 表の保存状態。案件の業務進捗status_codeとは別 |

## queryとページング

v1/v2の通常queryは limit（1〜199、既定50）、sort {field,direction}、filters配列、status、cursorを使います。filterは最大8個、opはeq / contains / gte / lteです。列が検索可能かはdefinitionで確認します。任意のSQL・正規表現・OR式は受け付けません。service queryは別契約でlimitとafterを使い、通常queryのfiltersをコピーしません。

next_cursorがnullになるまで、同じ条件と返されたcursorで続けます。CURSOR_STALEは蓄積したページを破棄して最初から再検索します。画面に古いページと新しいページを混在させません。v2一覧やごみ箱等にはafter / next_after、資産にはoffsetを使う経路もあります。各操作のschemaを優先してください。

## 変更監視・レート

changesはrevisionを確認するpollingで、SSEではありません。socket eventsもHTTPでcursorを送り、metadataのみのevents、has_more、次cursorを得ます。更新された行の内容は現在権限で改めて取得します。

表・appsの経路にはモジュール内同時2要求の制限があります。serviceは同時2要求と承認設定rpm（1〜120）。全経路共通の固定rpmは定義されていません。429はRetry-Afterが返れば従い、未設定なら待機を増やして回数上限付きで再試行します。詳しくは[エラー](https://mxd2024.github.io/claudia-partner-docs/v0.7/errors.html)。

## ログイン直後の反映待ち

新しい本人セッションは収集・DB反映の完了まで GET /v1/me が401 TOKEN_INVALIDになる場合があります。現collectorは**1回の処理完了後に15秒待機**します。固定15秒周期ではなく、収集・DB処理時間が加わります。外部収集に28秒の期限はありますが、全工程を包含する期限ではありません。**ログインから利用可能になるまでの保証上限・SLAは未定義**です。15秒、28秒、43秒以内の成功を保証しません。

正常に完了した新規ログイン直後で、同じ資格の GET /v1/me だけがTOKEN_INVALIDの場合に限り、回数と経過時間を限定して待機できます。クライアント待機枠の例は0.5秒間隔・最大20秒です。これは成功保証ではありません。20秒を超えたら待機を終了し、時刻・code・request_idを記録して環境管理者へ確認します。全401や変更操作を自動再送する規則ではなく、TOKEN_EXPIRED、明示失効、403、TLS/署名エラーには適用しません。

Coreのchecked_atの鮮度は5秒以内、reconciled_atは60秒以内を要求します。これらは古い認可情報を拒否する条件であり、新セッションの反映時間の約束ではありません。

## 操作別の認可条件の読み方

OpenAPIのx-required-authorityは主体、MFA、認証鮮度、required_capabilities、resource_checksを分けています。required_capabilitiesはCoreのAuthenticationRuleの値で、空配列でも無権限でよいとは限りません。管理DBの有効なservice_administratorやmanage_access、表・行・列の権限はresource_checksで別に宣言します。Coreに存在しないmanage_appsを要求条件として追加しません。

mfaは経路自体の条件、mfa_when_lifecycle_enabledとadministrative_session_when_lifecycle_enabledは本人ライフサイクル拡張が有効な環境の追加条件です。max_authentication_age_seconds=nullは操作固有の再認証時間上限なしを意味し、token・セッション・権限の有効期限を無視する意味ではありません。assetsはホストが固定した親資源の読取操作に認可を委譲するため、binding_rulesで条件が異なります。

## 再送方式

GET以外というだけでは変更操作とは限りません。検索・集計・計画POSTはread_or_planです。version/revisionは競合検出、fingerprintは確認済み計画との一致、Idempotency-Key/attempt_idは受領の識別に使います。移行開始・旧台帳採用はmigration_idと元の本文・fingerprintで既存結果を確認します。

各操作のx-retry-policyに方式・識別子・結果確認方法を掲載します。次表は改訂2でIdempotency-Keyが未宣言だった28操作の整理です。workspace.importには実装で必須のヘッダーを補いました。

table.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
table.export | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.import | write | Idempotency-Key | 同じキー・本文・前提版で再送し受領結果を確認する。現在権限も再検査する。競合時は最新状態と利用者の意図を照合し、版だけを置換しない。
workspace.export | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.exportRecords | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.aggregate | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.caseQuery | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspace.socket.events | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
asset.check | verification | none | GET /v1/assets/{namespace}/{resourceType}/{resourceId}/{assetId} で状態を確認。専用の再送識別子・応答再生保証なし。
service.permissions | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。
service.delete | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。
service.grantPut | write | version | GET /v2/access/grants/{subjectId}/{collection} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。
service.change | write | version | GET /v2/service-clients/{clientId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。
service.activate | write | none | GET /v2/service-clients/{clientId}（人の管理権限で照合） で状態を確認。専用の再送識別子・応答再生保証なし。
service.query | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
workspaceAccess.subjects | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
app-packages.migrationPreview | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
app-packages.migrationPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
app-packages.migrationBegin | write | fingerprint | 同じ主体・移行ID・本文・fingerprintで再送すると既存jobを返す。GET /v2/data-migrations/{migrationId} でも状態を確認。変更した入力やfingerprintでは再送しない。
app-packages.migrationCancel | write | version | GET /v2/data-migrations/{migrationId} で現在版・状態・対象値を確認。版は競合検出であり応答再生キーではない。未確定ならrequest_idで照会し、最新版を自動採用して再送しない。
app-packages.adoptionPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
app-packages.requirementsPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
app-packages.plan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
organization.settingsPlan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
organization.activity | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
apps.plan | read_or_plan | none | 同じ条件で取得可能。ただし一覧・計画・cursor・fingerprintは現在状態で変化する。計画を再取得しても適用は行わない。
identity.logoutSelf | write | attempt_id | 同じセッションとattempt_idで再送し失効受領を確認する。別attempt_idを自動発行しない。
