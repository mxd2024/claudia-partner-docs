# 公開開発者サイトの作業

- 編集元は `site-source/`、`v0.7/guide/*.md` と公開契約JSON。生成HTMLを手編集しない。
- `python tools/build_site.py` と `python tools/verify_site.py` を実行する。既存URLと操作アンカーを保持する。
- API契約を変更する場合は提供元の固定版から公開加工済みファイルを明示取り込みする。ブランチ先頭を稼働版とみなさない。
- 顧客別origin・資格・実データ・管理秘密経路・私有repoリンクを公開入力へ追加しない。例は架空にする。
- 配布済みの旧版と個別資料を削除しない。公開はdraft PRから差分と検証を確認する。
- 従来のインフラ側 `tools/public-docs.py stage` はこのサイトの更新入口ではない。契約の取り込み後、このrepoの生成器でサイトを再生成する。
