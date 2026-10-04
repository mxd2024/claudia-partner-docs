# 対応状況・バージョン

このドキュメントは **0.7.0-experimental** の公開契約を対象にしています。experimentalは仕様や提供条件が変更され得る段階を示します。

## 現在の範囲

API 132 operations / OpenAPI 132 operations / MCP 8 import tools

実装に存在するHTTPルート、OpenAPIが定義されたルート、MCPツールとして提供済みの機能は別の状態です。環境での有効化と呼出し元の権限も必要です。

## 機能別の対応状況

| 項目 | 現在の状態 |
| --- | --- |
| Core API | 実ルート132操作。機能ごとに有効化が必要 |
| OpenAPI | 132操作。実ルートと機械仕様を照合 |
| MCP取込アダプター | 8ツールを実装。対応する顧客アプリの接続契約が必要 |
| 全サービスMCP / BFF代替 | 対象として設計・受入を進行中 |
| 外部原本の画像参照 | API・保存アダプターあり。配備と原本到達性の確認が必要 |
| 正式本人セッション＋media Host | 統合配備の整備待ち |
| Dropboxフォルダー選択 / 共有URL解決 | 公開APIは未提供 |

## 管理アプリからのリンク

管理アプリは、利用するAPI版に対応した `/v0.7/` 配下のURLへリンクしてください。ページ内の操作リンクも同じ版に留まります。最新版へのリンクだけで利用中の仕様を置き換えないでください。

同じ対応版の説明訂正はこのサイト側で更新できます。APIの互換性が変わる場合は新しい版を追加し、旧版の説明を保持します。ルートの入口は最新の案内を示し、版別の入口は継続して利用できます。

## 更新・照合

この版の公開日は2026-10-04です。[公開manifest](https://mxd2024.github.io/claudia-partner-docs/v0.7/../manifest.json)にはドキュメント版と配布ファイルのSHA-256、[管理アプリ向けリンク定義](https://mxd2024.github.io/claudia-partner-docs/v0.7/../links.json)には安定したリンク先を記録します。

Markdown、OpenAPI、API一覧、MCPツール定義を同じ版に揃えて配信します。仕様にない機能を対応済みと扱わず、接続先の実際の提供状態と照合してください。

## 状態の読み方

implementedはソースに実装済み、experimentalは試験段階、optionalはHostでの有効化が必要、deployment-specificは配備ごとに提供状態が異なる意味です。文書へ掲載したことだけで稼働サイトへの配備を意味しません。

## ハッシュの意味

manifest.jsonの source_openapi_sha256 は公開処理前の元OpenAPIです。files["v0.7/openapi.json"] は、題名・公開説明を加工した配信ファイルそのもののSHA-256です。両者の不一致は加工によるもので、ダウンロードの完全性はfiles側と照合します。manifest自身は自己参照を避けるためfilesに含みません。

Windowsは Get-FileHash -Algorithm SHA256、macOSは shasum -a 256、Linuxは sha256sum で取得したファイルを照合できます。ZIPのSHAはZIP全体、内部ファイルのSHAは展開した各ファイルを対象とし、混同しません。

[変更履歴](https://mxd2024.github.io/claudia-partner-docs/v0.7/changelog.html)、[サポート](https://mxd2024.github.io/claudia-partner-docs/v0.7/operations.html)、[接続手順](https://mxd2024.github.io/claudia-partner-docs/v0.7/quickstart.html)を併せて確認してください。公開説明の整合検査と、利用環境での認証・MCP・実操作・独立担当の受入は別です。未実施の受入を完了として扱いません。
