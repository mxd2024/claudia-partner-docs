# BFF・運用・サポート

## BFFの責務

本人ログインの入口 /auth/login からIdPへ遷移し、登録済み /auth/callback でstateとPKCEを確認します。access/refresh tokenはサーバー側の保護ストアで保持し、ブラウザーには本人セッションcookieだけを渡します。実際のパスやcookie名は配布BFFの契約を確認してください。

cookieはSecure・HttpOnly・適切なSameSiteとし、書込要求は同じOriginとCSRF tokenを検査します。ブラウザーで扱うCSRF tokenとaccess tokenを混同しません。資格やcookieをURL・console.log・エラー画面へ出さないでください。

refreshはセッションごとに直列化し、rotationの永続化と再起動後の復元を行います。Coreの401を受けて無制限にrefreshを繰り返さず、失効・期限切れなら本人の再ログインへ戻します。403では認可を拡大せず、必要なMFAまたは管理者確認へ案内します。background pollingを本人の活動として偽装しません。

## 412と結果不明

412 VERSION_CONFLICTでは現在の権限で対象を再取得し、最新値と利用者の変更を比較します。利用者が解決した新しい操作だけに、新しいIdempotency-Keyを付けます。期待versionだけを自動的に置き換えて上書きしません。行が削除・不可視になっていれば404/403を扱います。

タイムアウト、接続断、OUTCOME_UNKNOWNは未実行の証明ではありません。対象・本文・期待版・Idempotency-Keyを保持し、同じ操作の照会または同じ内容の再送で確定結果を確認します。MCP取込はimports_status、アプリの適用は同じfingerprintとキーを使います。結果不明のまま別キーで二重実行しません。権限失効後など確認できない場合は管理者へ照会します。

## 更新とサポート

API版、ドキュメント版、配布クライアント版、実際の接続環境を別々に記録します。更新前には[変更履歴](https://mxd2024.github.io/claudia-partner-docs/v0.7/changelog.html)と[対応状況](https://mxd2024.github.io/claudia-partner-docs/v0.7/versions.html)を確認し、隔離した検証データで初回認証・読取・書込・失効を受け入れてから切り替えます。

不具合の相談には、API版、操作ID、時刻とタイムゾーン、HTTP status、code、request_id、再現手順、利用OS/クライアント版を添えます。access/refresh token、秘密鍵、cookie、顧客の行データは添えません。顧客環境の障害・権限・接続先は環境管理者の窓口へ連絡します。

共通ドキュメントの誤記は[公開Issue窓口](https://github.com/mxd2024/claudia-partner-docs/issues)へ報告できます。公開Issueに顧客接続先や資格を投稿しません。受付時間・SLA・廃止予告期間は現時点で公開契約として未確定です。
