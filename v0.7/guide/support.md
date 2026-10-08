# サポートと窓口

## 問い合わせの窓口

| 内容 | 窓口 |
| --- | --- |
| 接続情報の依頼（開発・検証用） | [接続情報を依頼する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/request-access.md)に、メールの窓口と雛形があります |
| 環境の障害、権限、接続先 | 環境管理者の窓口へ連絡します |
| このドキュメントの誤記 | [公開Issueの窓口](https://github.com/mxd2024/claudia-partner-docs/issues)へ報告できます。接続先や資格は、Issueに書かないでください |

障害対応の受付時間、SLA、廃止の予告期間は、未確定です。保証として扱わないでください。

## 不具合の相談に添える情報

次の情報を添えると、確認が早くなります。

- API版、操作ID
- 時刻とタイムゾーン
- HTTPステータス、code、`request_id`
- 再現の手順
- 利用しているOSとクライアントの版

**添えないもの**: アクセストークン、リフレッシュトークン、秘密鍵、cookie、顧客の行のデータ。

## 更新を受け入れるとき

API版、ドキュメントの版、配布クライアントの版、実際の接続環境を、別々に記録します。更新の前に、[変更履歴](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/changelog.md)と[対応状況とバージョン](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/versions.md)を確認します。切り替える前に、隔離した検証データで、最初の認証、読み取り、書き込み、失効を確認してください。
