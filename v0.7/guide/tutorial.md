# アプリの登録と運用

検証専用環境・検証データで実施する手順です。既存顧客データへそのまま適用しません。組織の管理者はMFAとcan_manage_access、表設計者は対象表のcan_design、利用者は必要なread/write/削除範囲を持つことを前提にします。[本人として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html)と、[HTTP・実行例](https://mxd2024.github.io/claudia-partner-docs/v0.7/examples.html)を先に確認してください。

## 1. 本人へ表の利用権を設定

管理者が `GET /v2/access/subjects` と `GET /v2/access/tables` で管理対象を確認し、`GET /v2/access/grants/{subjectId}/{collection}` の現在versionを取得します。PUTへ最新version、enabled、role、read_scope、write_scope、can_design、can_close、can_import、expires_atを送ります。初回version=0は現在grantがないことを取得して確認した場合だけ使います。expires_atは実施時点より未来の承認期限に置換します。

権限変更APIにIdempotency-KeyやIf-Matchを勝手に追加条件として仮定しません。この経路は本文versionを使います。利用者の新しい要求で許可・拒否を確認します。削除範囲は別のdelete-scope契約であり、write_scopeだけで削除できるとは限りません。

## 2. アプリを計画して登録

`POST /v2/apps/plan` にid、version、name、datasets、dependenciesを持つmanifestを送ります。ownedはアプリ所有表、sharedは既存共有表です。新規表にも事前の設計権が必要です。返ったchangesを確認し、同じmanifestと返されたfingerprintで `POST /v2/apps/apply` を実行します。Idempotency-Keyは必須です。例のaaaa…fingerprintを実際に送らないでください。

`GET /v2/apps/{appId}` と各表のdefinitionで登録結果を確認します。planからapplyまでに前提が変わったら競合として再計画・再確認します。アプリの登録は、画面のプログラムのアップロードや、サーバーへの配置を行いません。

## 3. 本人として作成・取得・更新

利用者の資格へ切り替え、definitionのschema_versionと書ける列を確認します。`POST /v2/tables/{collection}/batch` のcreateにvaluesを送ると、基盤がidと所有者を決めます。返ったid/versionを保存します。queryで取得し、updateにはそのid/versionを指定します。作成・更新は別のIdempotency-Keyを使います。

412では[競合・再送・復帰](https://mxd2024.github.io/claudia-partner-docs/v0.7/reliability.html)に従って再取得・比較・利用者確認へ進みます。操作結果が不明なだけの場合は同じキー・本文を保持します。

## 4. 関連を設定

子表に関連用の列を定義し、`PUT /v2/tables/{collection}/access` にmode、parent_collection、field、cardinalityを送ります。If-Matchは関連設定の現在version、Idempotency-Keyも必須です。親所属方式では親と子の現在権限を確認します。複数表を一括変更する /v2/transactions は最大8表・合計100行操作、既存親IDを使い、各表のschema_versionを指定します。

## 5. 削除と復元

deleteには行のid/versionと必要なreasonを送ります。ごみ箱の保持期間が設定されていること、本人の削除範囲を先に確認します。`GET /v2/tables/{collection}/trash` でtrash_idと現在versionを取得し、`POST /v2/tables/{collection}/trash/{trashId}/restore` にそのversion、reason、Idempotency-Keyを渡します。rowIdとtrashIdを取り違えません。定義変更や期限切れ、現在権限による拒否は自動回避しません。

## 6. 停止・再開

`GET /v2/apps/{appId}` のrevisionを取得し、`POST /v2/apps/{appId}/state` へaction=stop、revision、reasonを送ります。別のキーで現在revisionを使いaction=resumeを送ると再開します。停止・再開は行CRUDとは別です。trash/restore/detachも同じ状態APIですが、保持期間・依存先・現在状態に従います。復元直後はstoppedになり、必要な確認後に明示再開します。

## 7. service資格を設定して範囲を確認

[serviceとして接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/service-access.html)の手順に従い申請、承認、provision、private_key_jwt、activateを実施します。service queryの成功、許可外の列・表・操作の拒否、人用 /v1/me の拒否を確認します。writeを許可する場合はservice batch契約（最大50操作）を使い、本文の現在版とIdempotency-Keyを確認します。suspend/revoke後の旧資格拒否まで記録します。

## 8. 記録して終了

対象API版、環境、実施時刻、操作ID、HTTP/code/request_id、許可と拒否、再試行時の同じ操作識別子を記録します。資格・原本データは記録しません。
