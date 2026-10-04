# Claudia Partner 基盤 ― API・MCP 利用ガイド

Claudia Partner 基盤は、社内のデータ、権限、画像を、アプリケーションとAIエージェントに共通の窓口で提供します。アプリやAIエージェントは、この基盤に接続し、利用者の権限の範囲で、表や行を読み書きします。

このガイドは、基盤との**界面**、つまり接続の契約と手順をまとめたものです。基盤の内部の仕組みは説明しません。

> 対象は **0.7.0-experimental**（試験提供）です。仕様や提供条件は変更されることがあります。基盤の機能は、環境ごとに有効化されます。このサイトの閲覧にログインは不要ですが、基盤の利用には、認証と権限が必要です。

## 基盤が提供するもの

| 提供するもの | できること | 状態 |
| --- | --- | --- |
| データ | 表の定義、検索、行の追加・更新・削除、関連、ごみ箱と復元 | [環境による] |
| 権限 | 本人とserviceの認可、表・列・行の権限、組織の管理 | [環境による] |
| アプリ | アプリの登録、計画と適用、停止と再開 | [環境による] |
| 画像 | 画像を行に関連付けて表示。管理された原本と、外部の原本への参照 | [環境による] |
| AIエージェント（MCP） | 取込の操作（8ツール）。全APIサービスへの対応は準備中 | [提供中]（取込のみ） |

「環境による」は、ご利用の環境で有効化されているかどうかを、環境管理者に確認する必要があることを示します。状態の読み方は[基盤の考え方と責任分界](https://mxd2024.github.io/claudia-partner-docs/v0.7/principles.html)を参照してください。

## 想定する接続構成

アプリやAIエージェントは、利用者の権限を確認する窓口である**基盤API**に、本人またはserviceとして接続します。ログインは、認証サービスが担います。接続の形は、次の3つです。

```text
A. 人が使うアプリ（本人のログイン）
   利用者のブラウザー
     --(画面操作)--> アプリのサーバー側（BFF。トークンを保持）
     --(トークンを付けて呼び出す)--> 基盤API
   ログイン: アプリのサーバー側が利用者を認証サービスへ案内し（OIDC Authorization Code + PKCE、MFA）、認可コードをトークンに交換する。

B. サーバー処理（service接続）
   あなたのサーバー処理（登録した鍵を持つ）
     --(トークンを付けて呼び出す)--> 基盤API
   トークンは、登録した鍵で署名した要求を、認証サービスに送って取得する。serviceは人向けAPI（GET /v1/me など）を使えない。

C. AIエージェント（MCP）
   AIエージェント（MCPホスト）
     --(MCP)--> MCPアダプター（手元のPCで実行）
     --(HTTPS・接続キー)--> 管理サイト（取込の窓口）
     --(本人の権限で)--> 基盤API
   MCPアダプターの接続先は、基盤APIのURLではなく、管理サイトのHTTPS origin。現在のMCPは取込用8ツール。

基盤APIは、リクエストごとに、その時点の権限を確認する。
```

どの形でも、接続先のURL、資格、利用できる表は、環境ごとに環境管理者から受け取ります。このサイトには含まれません。

## 読者別の入口

| あなたは | 次に読むもの |
| --- | --- |
| 基盤を理解して、採用を判断したい | [基盤の考え方と責任分界](https://mxd2024.github.io/claudia-partner-docs/v0.7/principles.html) → [対応状況とバージョン](https://mxd2024.github.io/claudia-partner-docs/v0.7/versions.html) |
| 初めて接続する | [最初の接続の流れ](https://mxd2024.github.io/claudia-partner-docs/v0.7/quickstart.html) → [接続情報を依頼する](https://mxd2024.github.io/claudia-partner-docs/v0.7/request-access.html) |
| AIエージェントから使いたい | [MCPの導入](https://mxd2024.github.io/claudia-partner-docs/v0.7/mcp.html) |
| 実装を進めている | [共通ルール](https://mxd2024.github.io/claudia-partner-docs/v0.7/concepts.html) → [表とデータの更新](https://mxd2024.github.io/claudia-partner-docs/v0.7/tables.html) → [APIリファレンス](https://mxd2024.github.io/claudia-partner-docs/v0.7/api.html) |
| 用語を調べたい | [用語集](https://mxd2024.github.io/claudia-partner-docs/v0.7/glossary.html) |

## このサイトについて

このサイトは、説明と仕様の配信専用です。業務データをアップロードしたり、アクセストークンを入力したりする必要はありません。OpenAPIなどの機械可読な仕様は、[仕様ファイル](https://mxd2024.github.io/claudia-partner-docs/v0.7/specs.html)から入手できます。
