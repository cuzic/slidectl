# DOCUMENT Phase - ドキュメント化とコミット

TDDサイクルの DOCUMENT フェーズ：ドキュメントを整備してコミットします。

## このフェーズで行うこと

1. **コードドキュメントの確認**
   - モジュールのdocstringを確認・追加
   - クラスのdocstringを確認・追加
   - 関数のdocstringを確認・追加（引数、戻り値、例外）
   - 複雑な処理にコメントを追加

2. **READMEの更新（必要に応じて）**
   - 新機能を追加した場合は使用例を追加
   - セットアップ手順が変わった場合は更新

3. **変更のコミット**
   - 適切なコミットメッセージを作成
   - 関連issueを参照
   - テストとドキュメントも含める

4. **GitHubへプッシュ**
   - コミットをプッシュ
   - PRを作成（必要に応じて）
   - issueを更新

5. **Issue の更新**
   - タスクリストにチェック
   - 進捗をコメント
   - 完了した場合はissueをclose

## Docstring フォーマット

```python
def calculate_density(text_area: float, slide_area: float) -> float:
    """スライドの文字密度を計算する。

    文字密度は、テキスト領域の合計面積をスライド全体の面積で割った値です。

    Args:
        text_area: テキスト領域の合計面積（px²）
        slide_area: スライド全体の面積（px²）

    Returns:
        文字密度（0.0〜1.0の範囲）

    Raises:
        ValueError: slide_areaが0以下の場合

    Examples:
        >>> calculate_density(1000, 100000)
        0.01
    """
    if slide_area <= 0:
        raise ValueError("slide_area must be positive")
    return text_area / slide_area
```

## コミットメッセージフォーマット

```
<type>: <subject>

<body>

<footer>
```

### Type
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `docs`: ドキュメント
- `style`: フォーマット
- `chore`: その他

### 例

```
feat: ワークスペース管理機能を実装

- ワークスペースディレクトリ構造の定義
- 初期化機能の実装
- パス解決ヘルパー関数の追加
- ユニットテストを追加（カバレッジ95%）

Closes #5
```

## チェックリスト

### ドキュメント
- [ ] モジュールdocstringを追加
- [ ] クラスdocstringを追加
- [ ] 関数docstringを追加（Args, Returns, Raises）
- [ ] 必要な箇所にコメント追加
- [ ] READMEを更新（必要に応じて）

### Git操作
- [ ] 変更をステージング（`git add`）
- [ ] コミットメッセージを作成
- [ ] コミット実行
- [ ] GitHubにプッシュ

### Issue管理
- [ ] タスクリストにチェック
- [ ] 進捗コメントを追加
- [ ] 完了時はissueをclose

## Git コマンド例

```bash
# 変更を確認
git status
git diff

# ステージング
git add src/slidectl/workspace.py tests/test_workspace.py

# コミット
git commit -m "feat: ワークスペース管理機能を実装

- ワークスペースディレクトリ構造の定義
- 初期化機能の実装
- ユニットテストを追加

Closes #5"

# プッシュ
git push origin main
```

## Issue コメント例

```markdown
## 実装完了

ワークスペース管理機能を実装しました。

### 実装内容
- [x] ワークスペース構造の定義
- [x] ディレクトリ初期化関数
- [x] パス解決ヘルパー関数
- [x] ユニットテスト（カバレッジ95%）

### テスト結果
すべてのテストがパスしました。
\`\`\`
test_workspace.py::test_workspace_initialization PASSED
test_workspace.py::test_workspace_validation PASSED
Coverage: 95%
\`\`\`

### 次のステップ
設定ファイル管理（#6）に進みます。
```

## 次のステップ

ドキュメント化とコミットが完了したら、次の機能の実装に進みます。
新しいサイクルは PLAN フェーズから始めます。
