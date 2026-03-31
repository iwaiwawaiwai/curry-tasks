# 開発プロジェクト 運用ガイド

## フォルダ構成

```
VSCode/                        ← ワークスペース（作業場）
├── brain/                     ← 第二の脳（GitHub: second-brain）
├── projects/                  ← 開発プロジェクト置き場
│   ├── (プロジェクト名)/      ← 各プロジェクトが独立したGitリポジトリ
│   └── ...
└── CLAUDE.md
```

## Gitリポジトリの運用

- **brain** と **各プロジェクト** は別々のGitリポジトリとして管理する
- プロジェクトを新しく作るときは `projects/` の直下に配置する
- 各プロジェクトは GitHub に独立したリポジトリを持つ

### リポジトリ一覧

| リポジトリ名 | 用途 | GitHub |
|---|---|---|
| second-brain | brain・CLAUDE.md の管理 | iwaiwawaiwai/second-brain |
| kaorilogo-prototype | KAORILOGOチャットボット | iwaiwawaiwai/kaorilogo-prototype |

## 新しいプロジェクトを始めるときの手順

1. `projects/(プロジェクト名)/` フォルダを作成
2. `git init` で新しいリポジトリを初期化
3. `.gitignore` を作成（node_modules、.env など除外）
4. `gh repo create` で GitHub にリポジトリを作成・push
5. 必要ならデプロイ先（Railway など）と連携

## デプロイ

- **Railway** を使う（Node.js/Expressアプリはそのまま動く）
- 環境変数（APIキーなど）は Railway の管理画面で設定
- GitHubリポジトリと連携することで、pushのたびに自動デプロイされる

## 命名規則

- フォルダ名・リポジトリ名：ハイフン区切り（例：`kaorilogo-prototype`）
- 本番用とプロトタイプは `-prototype` で区別する
