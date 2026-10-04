# 最初の接続の流れ

最初のAPI呼び出しが成功するまでを、3つのステップで示します。各ステップの詳細は、リンク先のページにあります。

## ステップ1　接続情報を依頼する

環境管理者に、接続先のURL、認証サービスの情報、本人用のクライアントなどを依頼します。受付の確認（一次回答）は、翌営業日を目標にしています。接続情報を受け取れる日は、申請の内容を確認した後に案内されます。

**できたこと**: 接続に必要な値が、すべてそろっている。

詳しくは、[接続情報を依頼する](https://mxd2024.github.io/claudia-partner-docs/v0.7/request-access.html)。

## ステップ2　本人として接続する

受け取った情報でログイン（OIDC + PKCE）し、アクセストークンを取得します。`GET /v1/me`を呼びます。

**できたこと**: `GET /v1/me`が、200で、本人のidと権限を返す。

詳しくは、[本人として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html)。人の操作を介さない処理は、[serviceとして接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/service-access.html)。

## ステップ3　最初の読み書きをする

表の一覧を取得し、定義を読み、検索へ進みます。次に、検証用の表で、行の追加と更新を試します。

**できたこと**: 検証用の表で、行を読み、書ける。

詳しくは、[表とデータの更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/tables.html)。

## うまくいかないとき

| 症状 | 確認すること |
| --- | --- |
| ログイン直後に、401（`TOKEN_INVALID`）になる | 数秒から十数秒の反映待ちの可能性があります。[本人として接続する](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html)の「ログイン直後の反映待ち」を参照 |
| 401が続く | 接続先、client_id、期限、セッションを確認 |
| 403 | 現在の権限と、MFAを確認 |
| TLSの検証に失敗する | 検証を無効にせず、環境管理者が交付した証明書を使う |

エラーの一覧は、[エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/errors.html)。

## 文書の例について

文書の例は、合成のデータです。実際に接続できるかは、環境ごとに、最初の接続で確認してください。
