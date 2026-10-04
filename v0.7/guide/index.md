# API・MCP 利用ガイド

Claudia Partner のデータ、権限、画像を、アプリケーションやAIエージェントから利用するための共通ドキュメントです。管理画面の操作とは独立して、接続に必要な仕様を確認できます。

> 対象は **0.7.0-experimental**。記載されたAPIは環境ごとに有効化されます。この説明サイトへのアクセスにログインは不要ですが、業務APIの利用には認証と権限が必要です。

初回は[最初のAPI接続](https://mxd2024.github.io/claudia-partner-docs/v0.7/quickstart.html)から進みます。[概念](https://mxd2024.github.io/claudia-partner-docs/v0.7/concepts.html)、[アプリ登録から運用まで](https://mxd2024.github.io/claudia-partner-docs/v0.7/tutorial.html)、[変更履歴](https://mxd2024.github.io/claudia-partner-docs/v0.7/changelog.html)も参照できます。

## 目的から探す

| やりたいこと | 読む資料 |
| --- | --- |
| アプリを接続し、本人の権限で利用する | [認証・権限](https://mxd2024.github.io/claudia-partner-docs/v0.7/authentication.html) |
| 表を検索し、行を追加・更新する | [表・データ更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/tables.html) |
| デザイン画像やDropbox原本を関連付ける | [画像・Dropbox連携](https://mxd2024.github.io/claudia-partner-docs/v0.7/media.html) |
| AIエージェントから業務操作を行う | [AIエージェント・MCP](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html) |
| パス、入力、応答の仕様を調べる | [APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/api.html) |
| エラーから復帰する | [エラーと再試行](https://mxd2024.github.io/claudia-partner-docs/v0.7/errors.html) |

## 接続までの流れ

1. 環境管理者から、対象環境のHTTPS接続先、対応版、有効機能、認証方式を確認します。
2. 本人ログインか、承認されたserviceによる接続かを決めます。管理権限と業務データの利用権限は別に確認します。
3. [APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/api.html)で対象操作と入力・応答を確認し、合成データの環境で許可と拒否の両方を試します。
4. 更新時の競合、認証更新、失効、通信中断からの再開を確認してから利用を開始します。

APIの仕様は公開されていますが、接続先・資格・利用可能な表は契約する環境ごとに異なります。このサイトには個別環境の資格や顧客データを含めていません。

## アプリとエージェントの共通基盤

表・列・行の操作、添付、関連、サービス権限、組織管理を共通APIで扱います。MCPの対象もこれらすべての公開APIサービスです。現在のMCPアダプターの実装範囲は取込用8ツールで、全サービスへの対応は[対応状況](https://mxd2024.github.io/claudia-partner-docs/v0.7/versions.html)に区別して記載しています。

## 仕様を取得する

- [OpenAPI 3.1 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/openapi.json)：機械可読な132操作の入力・応答・認証定義。
- [全API一覧 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/api-inventory.json)：実ルート132操作と機械仕様の整備状況。
- [現行MCPツール定義 JSON](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp-tools.json)：取込アダプターの8ツール。
- [このガイドのMarkdown](https://mxd2024.github.io/claudia-partner-docs/v0.7/guide/index.md)：AIやテキストツールからの参照用。

このサイトは説明と仕様の配信専用です。ここへ業務データをアップロードしたり、アクセストークンを入力したりする必要はありません。
