# 最初の接続の流れ

基盤に初めて接続するときの、全体の流れです。最初のAPI呼び出しが成功するまでを、3つのステップに分けて示します。

接続の方法には、利用者としての接続と、serviceとしての接続があります。ここでは、利用者としての接続を例にします。利用者とserviceの違いは、[用語集](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/glossary.md)にあります。

## ステップ1　接続情報を依頼する

基盤の接続先や、ログインの設定は、環境ごとに違います。まず、環境管理者に、接続情報を依頼します。

- 受付の確認（一次回答）は、翌営業日を目標にしています。
- 接続情報を受け取れる日は、申請の内容を確認した後に案内されます。

**できたこと**: 接続に必要な値が、すべてそろった。

詳しくは、[接続情報を依頼する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/request-access.md)。

## ステップ2　利用者として接続する

受け取った情報で、利用者のログインを行い、アクセストークンを取得します。そのトークンで、`GET /v1/me`を呼びます。`GET /v1/me`は、「いま、誰として接続しているか」を返すAPIです。

**できたこと**: `GET /v1/me`が200で、利用者のidと権限を返した。

詳しくは、[利用者として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/authentication.md)。人の操作なしに動く処理は、[serviceとして接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/service-access.md)。

## ステップ3　最初の読み書きをする

表の一覧を取得し、表の定義を読んで、検索します。次に、検証用の表で、行の追加と更新を試します。

**できたこと**: 検証用の表で、行を読み、書けた。

詳しくは、[表とデータの更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/tables.md)。

## うまくいかないとき

| 症状 | 確認すること |
| --- | --- |
| ログインの直後に、401（`TOKEN_INVALID`）になる | 数秒から十数秒の、反映待ちの可能性があります。[利用者として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/authentication.md)の「ログイン直後の反映待ち」を参照 |
| 401が続く | 接続先、client_id、有効期限、セッションを確認 |
| 403 | 現在の権限と、MFAを確認 |
| TLSの検証に失敗する | 検証を無効にせず、環境管理者が渡した証明書を使う |

エラーの一覧は、[エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/errors.md)にあります。

## 文書の例について

文書の例は、合成のデータです。実際に接続できるかは、環境ごとに、最初の接続で確認してください。
