# TDD Slash Commands

このディレクトリには、TDD（Test-Driven Development）サイクルに沿った開発を支援するカスタムスラッシュコマンドが含まれています。

## 🔄 TDDサイクル

```
PLAN → RED → GREEN → REFACTOR → VERIFY → DOCUMENT → (次のサイクルへ)
 📋     🔴     🟢       🔧         ✅         📝
```

## 📚 利用可能なコマンド

### `/tdd`
TDDサイクル全体のガイド。各フェーズの説明と流れを確認できます。

### `/plan`
**Phase 1: 実装計画**
- GitHub issueの読み込み
- タスクの理解と計画策定
- ファイル構成とインターフェース設計
- タスクリストの作成

```
/plan
```

### `/red`
**Phase 2: テストファースト**
- テストファイルの作成
- 失敗するテストの作成
- テスト実行と失敗確認

```
/red
```

### `/green`
**Phase 3: 最小実装**
- テストをパスする最小限の実装
- テスト実行とパス確認

```
/green
```

### `/refactor`
**Phase 4: コード改善**
- コードの整理・改善
- 命名の改善、型ヒント追加
- 継続的なテスト実行

```
/refactor
```

### `/verify`
**Phase 5: 品質確認**
- すべてのテスト実行
- Linter、型チェック実行
- カバレッジ確認

```
/verify
```

### `/document`
**Phase 6: ドキュメント化**
- Docstring追加
- READMEの更新
- コミットとプッシュ
- Issue更新

```
/document
```

## 🎯 使い方の例

### Issue #5 を実装する場合

1. **計画を立てる**
   ```
   /plan
   ```
   → issue #5（ワークスペース構造とディレクトリ管理）を確認し、実装計画を立てる

2. **テストを書く（RED）**
   ```
   /red
   ```
   → `tests/test_workspace.py` を作成し、失敗するテストを書く
   → `mise run test` で失敗を確認

3. **実装する（GREEN）**
   ```
   /green
   ```
   → `src/slidectl/workspace.py` を実装
   → `mise run test` でテストがパスすることを確認

4. **リファクタリング（REFACTOR）**
   ```
   /refactor
   ```
   → コードを整理、命名改善、型ヒント追加
   → `mise run test` と `mise run lint` を実行

5. **検証（VERIFY）**
   ```
   /verify
   ```
   → すべてのテスト実行
   → カバレッジ確認
   → Linter、型チェック実行

6. **ドキュメント化（DOCUMENT）**
   ```
   /document
   ```
   → Docstring追加
   → コミット・プッシュ
   → Issue #5 を更新

7. **次のIssueへ**
   → `/plan` で次のサイクルを開始

## 💡 ベストプラクティス

### Small Steps（小さなステップ）
- 1つのissueを小さなタスクに分割
- 各タスクで1サイクル回す
- 頻繁にコミットする

### Test First（テストファースト）
- 必ずテストを先に書く
- テストで仕様を明確にする
- RED → GREEN の順序を守る

### Refactor Fearlessly（恐れずにリファクタリング）
- テストがあるので安心してリファクタリング
- コードの品質を継続的に向上
- 既存機能を壊さないことを確認

### Commit Often（頻繁にコミット）
- 各フェーズでコミット
- 小さな変更で頻繁にコミット
- コミットメッセージを明確に

## 🔧 関連コマンド

```bash
# テスト実行
mise run test

# Linter実行
mise run lint

# フォーマット
mise run format

# すべてのチェック
mise run test && mise run lint
```

## 📖 参考資料

- [要件定義](../../docs/requirements.md)
- [技術仕様](../../docs/spec.md)
- [データフロー仕様](../../docs/dataflow.md)
- [GitHub Issues](https://github.com/cuzic/slidectl/issues)
