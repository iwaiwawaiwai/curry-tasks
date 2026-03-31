# シーン選択カード用 画像生成プロンプト集

生成後の保存先: `kaorilogo-prototype/public/images/scenes/{key}.png`
推奨アスペクト比: **4:3**（横長カード用）

---

## 共通スタイル指定（全プロンプトの末尾に付ける）

```
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

## 各シーンのプロンプト

### work.png（仕事中・在宅ワーク）

```
A serene minimalist home office desk with soft morning sunlight streaming through a window.
A laptop, a small potted green plant, a white ceramic mug, and neatly arranged papers.
Warm neutral tones — ivory, beige, and light wood. Clean and focused atmosphere.
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

### sleep.png（寝る前・寝室）

```
A cozy Japanese-style bedroom at night with a dim warm bedside lamp.
Soft white linen pillows, a light linen duvet, and a small aroma diffuser with gentle mist.
Dark indigo and warm cream tones. Peaceful and deeply relaxing atmosphere.
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

### relax.png（リビングでくつろぐ）

```
A comfortable living room with soft afternoon light filtering through sheer curtains.
A plush linen sofa with cushions, a low wooden coffee table, and a small bouquet of dried flowers.
Warm beige and terracotta tones. Relaxed and inviting home atmosphere.
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

### outdoor.png（外出・お出かけ）

```
A quiet tree-lined path in a Japanese park during a calm morning.
Soft dappled sunlight through fresh green leaves, a gentle breeze hinting at movement.
Light green and warm golden tones. Refreshing and serene outdoor atmosphere.
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

### gift.png（ギフト・プレゼント用）

```
An elegantly wrapped gift box with a soft satin ribbon,
surrounded by delicate dried lavender sprigs and small flowers on a light linen surface.
Soft pink, beige, and ivory tones. Minimal luxury gift aesthetic.
soft natural lighting, warm and minimal Japanese aesthetic, no people, photography style, high quality
```

---

## 画像の使い方

生成した画像を以下のパスに配置するだけで自動的に反映されます：

| ファイル名 | シーン |
|---|---|
| `public/images/scenes/work.png` | 仕事中・在宅 |
| `public/images/scenes/sleep.png` | 寝る前・寝室 |
| `public/images/scenes/relax.png` | リビングでくつろぐ |
| `public/images/scenes/outdoor.png` | 外出・お出かけ |
| `public/images/scenes/gift.png` | ギフト・プレゼント用 |

画像がない場合は絵文字のグラデーション背景にフォールバックします。
