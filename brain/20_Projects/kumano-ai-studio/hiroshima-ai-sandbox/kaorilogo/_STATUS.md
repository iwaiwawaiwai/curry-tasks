# KAORILOGOプロトタイプ — 現状ステータス

最終更新: 2026-03-24
現在フェーズ: **ステップ4（動作確認・品質改善）**

---

## 起動方法

```bash
cd /Users/iiwabook/VSCode/kaorilogo-prototype
ANTHROPIC_API_KEY="sk-ant-api03-..." node server.js
```
→ ブラウザで `http://localhost:3000`

---

## 現在の実装状態

| 項目 | 内容 |
|---|---|
| モデル | claude-sonnet-4-6 |
| max_tokens | 2048 |
| 推薦件数 | 上位5件（内部で全13商品スコアリング） |
| エージェント | hearing / proposal / closing（自律切替） |
| モード移行 | filled_axes >= 4 で hearing → proposal |

### 商品（13件）

- Life of Aromaブレンド: ON Time / OFF Time / All Time / 認知AM / 認知PM
- エッセンシャルオイル: ラベンダー / ローズマリー / レモン / ベルガモット / ペパーミント
- KAORILOGOオリジナル: 瀬戸の香 / 鶴香・未来 / Upcycled Citron

---

## ファイル構成

```
kaorilogo-prototype/
├── server.js       ← メインロジック（AIプロンプト・API・推薦ロジック）
├── public/
│   └── index.html  ← チャットUI（2カラム）
└── package.json

projects/kaorilogo/
├── kaorilogo-data-schema.html  ← データスキーマ定義書（最新版）
├── kaorilogo-data-schema.png   ← 旧スクリーンショット（更新前）
└── kaorilogo-products.json     ← 商品データ（本番実装時用）
```

---

## 次回やること

- [ ] UIの確認・デザイン調整（KAORILOGOサイトの色調・ロゴとの調和）
- [ ] 推薦カードのデザイン改善
- [ ] 変更をgitコミット

---

## 開発ロードマップ

| # | ステップ | 状態 |
|---|---|---|
| 1 | 商品データ整理・推薦軸設計 | ✅ 完了 |
| 2 | AIプロンプト設計 | ✅ 完了 |
| 3 | プロトタイプ作成（Node.js版） | ✅ 完了 |
| 4 | 動作確認・品質改善 | 🔄 **現在** |
| 5〜 | BASEサイト連携・本番実装 | ⬜ 受注後に判断 |
