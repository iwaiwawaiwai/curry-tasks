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

## 次回やること（2026-03-25）

- [ ] 今日の変更をgitコミット（ストリーミング対応・UI修正一式）
- [ ] 動作確認（ストリーミング・改行・各UI修正）
- [ ] 香りロゴさんへのヒアリング：ブレンドオイル成分の確認（_STATUS.md 下部参照）

---

## ⚠️ ヒアリング確認事項（香りロゴさんへ）

### ブレンドオイルの正式成分

現在 `index.html` の `PRODUCT_META` に暫定成分を `verified: false` で入力済み。
UIには「⚠️ 暫定」バッジが表示されている。

**次回ヒアリング時に各商品の実際の配合香料を確認して更新すること。**

| 商品名 | 暫定成分（要確認） |
|---|---|
| ON Time | ローズマリー・レモン・スペアミント・ユーカリ |
| OFF Time | ラベンダー・スイートオレンジ・グレープフルーツ・ホーリーフ |
| All Time | マンダリン・スイートオレンジ・レモン・プチグレン |
| 認知AM | ローズマリー・レモン・スペアミント・ユーカリ |
| 認知PM | ラベンダー・ベルガモット・オレンジスイート |
| 瀬戸の香 | 広島産レモン・サイプレス・シダーウッド・ローズマリー |
| 鶴香・未来 | レモン・ライム・グレープフルーツ |
| Upcycled Citron | 広島産レモン・ローズマリー・ティアレ・ムスク |

確認後は `index.html` の該当商品を `verified: true` に更新し、成分リストを修正する。

---

## 開発ロードマップ

| # | ステップ | 状態 |
|---|---|---|
| 1 | 商品データ整理・推薦軸設計 | ✅ 完了 |
| 2 | AIプロンプト設計 | ✅ 完了 |
| 3 | プロトタイプ作成（Node.js版） | ✅ 完了 |
| 4 | 動作確認・品質改善 | 🔄 **現在** |
| 5〜 | BASEサイト連携・本番実装 | ⬜ 受注後に判断 |
