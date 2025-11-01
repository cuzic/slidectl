# slidectl

非LLMスライド生成オーケストレータ

## 概要

slidectlは、Markdown形式の講演原稿から高品質なスライドを自動生成するCLIツールです。LLMによる内容生成と、Playwrightによる品質測定・最適化を組み合わせ、見やすく情報密度が適切なスライドを生成します。

## 主な機能

- **原稿の構造化**: Markdown原稿を解析し、スライド構造を抽出
- **スライド生成**: LLM連携によるMarpスライドの自動生成
- **品質測定**: Playwrightによる文字密度・余白・重なりの定量評価
- **自動最適化**: 測定結果に基づく反復的な品質改善
- **PPTX出力**: 最終的なプレゼンテーションファイルの生成

## 技術スタック

- **言語**: Python 3.11+
- **パッケージ管理**: uv
- **ランタイム/タスク管理**: mise
- **レンダリング**: marp-cli (Node)
- **DOM解析・計測**: Playwright (Chromium)
- **CLI**: Typer

## セットアップ

### 前提条件

- [mise](https://mise.jdx.dev/) - ランタイム管理ツール
- [uv](https://docs.astral.sh/uv/) - Python パッケージマネージャー

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/cuzic/slidectl.git
cd slidectl

# Python と Node.js をインストール
mise install

# 依存関係をインストール（uv venv, pip install, playwright install, npm install）
mise run setup
```

### 動作確認

```bash
# CLIヘルプを表示
uv run slidectl --help

# バージョン確認
uv run slidectl --version

# 利用可能な mise タスクを確認
mise tasks
```

## 使い方

### ワークスペースの初期化（未実装）

```bash
mise run init
# または
uv run slidectl init --ws workspace
```

### パイプライン全体の実行（未実装）

```bash
mise run pipeline
```

これは以下のコマンドを順次実行します：

1. `ingest` - 原稿の構造化
2. `instruct` - LLMへの指示生成
3. `build` - Marpスライド生成
4. `render` - HTML/PPTX レンダリング
5. `measure` - 品質測定
6. `optimize` - 最適化ループ（最大3回）
7. `export` - 最終PPTX出力

### 個別コマンド実行（未実装）

```bash
# 原稿の構造解析
uv run slidectl ingest --ws workspace --in doc/raw.md

# 状態確認
uv run slidectl status --ws workspace
```

### 開発タスク

```bash
# テスト実行
mise run test

# Linter実行
mise run lint

# コードフォーマット
mise run format

# ワークスペースをクリーンアップ
mise run clean
```

## 開発

### TDD サイクルで開発

このプロジェクトはTDD（Test-Driven Development）で開発されています。
カスタムスラッシュコマンドを使って、効率的に開発できます。

#### TDDサイクル

```
PLAN → RED → GREEN → REFACTOR → VERIFY → DOCUMENT
 📋     🔴     🟢       🔧         ✅         📝
```

#### 使い方

**方法1: `/tdd` で全フェーズを自動実行（推奨）**

```bash
# すべてのフェーズを順次実行
/tdd
```

このコマンド1つで、issue の読み込みから実装、テスト、リファクタリング、品質確認、ドキュメント化、コミット・プッシュまでを完了できます。各フェーズで確認を取りながら進めます。

**方法2: 個別フェーズの実行**

特定のフェーズだけを実行したい場合：

```bash
/plan      # 1. 実装計画を立てる
/red       # 2. テストを書く（失敗するテスト）
/green     # 3. 実装する（テストをパス）
/refactor  # 4. リファクタリング
/verify    # 5. 品質確認
/document  # 6. ドキュメント化とコミット
```

詳細は [.claude/commands/README.md](.claude/commands/README.md) を参照してください。

### GitHub Issues

実装すべき機能は [GitHub Issues](https://github.com/cuzic/slidectl/issues) で管理されています。

- **Epic Issues**: 大きな機能単位（#1〜#4）
- **Feature Issues**: 個別の実装タスク（#5〜#23）

実装の順序は issues の説明を参照してください。

## ドキュメント

詳細な仕様は以下を参照してください：

- [要件定義](docs/requirements.md)
- [技術仕様](docs/spec.md)
- [データフロー仕様](docs/dataflow.md)

## ステータス

🚧 現在開発中

## ライセンス

TBD
