# 広島AIサンドボックス 課題データ 構成情報

このプロジェクトには206件の課題データが含まれています。
データ量が多いため、Claudeは指示があるまでファイルを全件読み込まないでください。

## ファイル構成とスコープ

1. **HIROSHIMA-AISandBox_index.jsonl**
   - 項目: id, title, industry, impact
   - 用途: 全体の検索・フィルタリングに使用する

2. **HIROSHIMA-AISandBox_main_challenge.jsonl**
   - 項目: id, challenge_details（課題詳細）
   - 用途: 具体的な課題内容の分析に使用する

3. **HIROSHIMA-AISandBox_context.jsonl**
   - 項目: id, company_name, business, available_data, overview
   - 用途: 企業情報・背景の確認に使用する

## 運用ルール

- 検索時は `grep` や `sed` 等のツールを使用して、必要なIDだけを特定して読み取ること
- ユーザーから特定のIDの指示があるまで、全ファイルを一度に読み込まないこと
