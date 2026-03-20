# AIエージェントの設計パターン - Deep Research

> 作成日: 2026-03-05
> ステータス: 要熟成 → 30_Tech_Notes/ へ移動候補

---

## brain内の既存知識

**未記録** - このテーマに関するノートはbrain内に存在しない。本ノートが初出。

---

## 1. 基礎定義：AIエージェントとは

LLMを中核に持ち、以下を自律的に行うシステム：
- **推論**（Reasoning）
- **計画**（Planning）
- **ツール呼び出し**（Tool Calling）
- **記憶**（Memory）
- **自己修正**（Self-correction）

> 2025年は「AI Agent元年」と呼ばれ、企業システムへの本格普及が始まった。

---

## 2. Andrew Ng の 4大設計パターン（信頼度：高）

Andrew Ng（DeepLearning.AI）が定義した、最も影響力のある分類。

| パターン | 概要 |
|---------|------|
| **Reflection（反省）** | エージェントが自分の出力を批評し改善する。最も基本的だが効果大 |
| **Tool Use（ツール利用）** | Web検索・コード実行・API呼び出しなど外部ツールを使う |
| **Planning（計画）** | 複雑タスクを実行可能なステップに分解する |
| **Multi-Agent Collaboration** | 専門化した複数エージェントが協調して複雑ワークフローを処理 |

出典: [Andrew Ng on X](https://x.com/AndrewYNg/status/1773393357022298617)

---

## 3. 主要アーキテクチャパターン（信頼度：高）

### 3-1. ReAct（Reasoning + Acting）
- **構造**: Thought → Action → Observation のループ
- **特徴**: Chain-of-thoughtとツール利用を統合。ハルシネーション低減効果あり
- **弱点**: 複雑な多ステップタスクでは遅延・失敗が起きやすい

### 3-2. Plan-and-Execute
- **構造**: 計画フェーズ → 実行フェーズ（失敗時のみ再計画）
- **特徴**: ReActより高速・高精度。LLM呼び出し回数を削減
- **使い所**: 複雑な多ステップワークフロー

### 3-3. Reflexion（自己反省）
- 実行後に言語フィードバックで計画を批評・修正
- Reflection パターンの具体的実装の一つ

### 3-4. Orchestrator-Worker
- オーケストレーターがタスク分解し、ワーカーエージェントに委譲
- マルチエージェントの基本構造

### 3-5. Supervisor + Peer型
- **Supervisor型**: 中央管理エージェントが他を統括（集中管理）
- **Peer型**: 全エージェントが対等に直接通信（分散）

出典: [Google Cloud Design Patterns](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system), [MachineLearningMastery](https://machinelearningmastery.com/7-must-know-agentic-ai-design-patterns/)

---

## 4. メモリ管理パターン（信頼度：中）

| タイプ | 説明 |
|-------|------|
| **In-context memory** | プロンプト内の短期記憶 |
| **External memory（RAG）** | ベクトルDBなど外部ストアからの検索 |
| **Episodic memory** | 過去のインタラクション履歴 |
| **Autonomous memory orchestration** | LLM自身がメモリ管理ツールを操作（最新トレンド）|

**Context Engineering** という新概念が登場：コンテキストを管理リソースとして扱い、取得・フィルタリング・整形を最適化する設計思想。

出典: [Serokell - LTM Design Patterns](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures)

---

## 5. オーケストレーションフレームワーク比較（信頼度：中）

| フレームワーク | 特徴 | 課題 |
|-------------|------|-----|
| **LangGraph** | グラフベース、状態差分のみ転送→最速・最小トークン | 学習コスト高 |
| **LangChain** | フル会話履歴保持→トークン消費大 | マルチエージェントで重い |
| **AutoGen** | 一貫した協調動作 | 中程度の遅延 |
| **CrewAI** | 自律的な熟慮プロセス→最大遅延 | 速度が課題 |

出典: [SitePoint - Orchestration Wars 2026](https://www.sitepoint.com/agent-orchestration-framework-comparison-2026/)

---

## 6. 自己修正・Reflection の実装パターン（信頼度：高）

```
[出力生成] → [Critic/Evaluator] → [修正判断] → [再生成 or 完了]
```

- **Self-critique**: 同一LLMが自己批評
- **外部ツール検証**: コード実行結果でグラウンディング
- **Critic Agentパターン**: 専用の批評エージェントを設置
- **リアルタイム誤差検出**: ステップ単位での自動評価（カスケード障害防止）

出典: [SitePoint - Agentic Design Patterns 2026](https://www.sitepoint.com/the-definitive-guide-to-agentic-design-patterns-in-2026/)

---

## 7. 複合パターンの例（本番システム）

```
Orchestrator-Worker（タスク分解）
  └── Worker A: Reflection（自己修正）+ Tool Use（外部データ取得）
  └── Worker B: ReAct（動的推論）
  └── Worker C: Plan-and-Execute（確定的タスク）
```

---

## 8. 2026年トレンド・展望（信頼度：中）

- **Context Engineering** の設計哲学が主流化
- **Human-in-the-loop** が倫理・安全担保の標準手法に
- **評価駆動アーキテクチャ**: Evaluatorをコア要素として設計
- **自律メモリ管理**: エージェント自身がメモリを管理
- マルチエージェントの活用が企業レベルで本格化

---

## 9. 参照文献

- [Andrew Ng - 4 Agentic Design Patterns](https://x.com/AndrewYNg/status/1773393357022298617)
- [Google Cloud - Choose a design pattern](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)
- [Microsoft Azure - AI Agent Design Patterns](https://learn.microsoft.com/ja-jp/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [SitePoint - Agentic Design Patterns 2026](https://www.sitepoint.com/the-definitive-guide-to-agentic-design-patterns-in-2026/)
- [MachineLearningMastery - 7 Must-Know Patterns](https://machinelearningmastery.com/7-must-know-agentic-ai-design-patterns/)
- [Serokell - LTM Design Patterns](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures)
- [ByteByteGo - Agentic Workflow Patterns](https://blog.bytebytego.com/p/top-ai-agentic-workflow-patterns)
- [Zenn - AIエージェント設計原則2025](https://zenn.dev/r_kaga/articles/e0c096d03b5781)

---

## 次のアクション候補

- [ ] 熊野AIスタジオのシステム設計に適用できるパターンを検討
- [ ] 30_Tech_Notes/ai-agent-patterns.md として知識化
- [ ] 実装フレームワーク選定（LangGraph vs AutoGen）の深掘り
