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
