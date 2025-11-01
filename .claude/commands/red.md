# RED Phase - テストファースト

TDDサイクルの RED フェーズ：失敗するテストを書きます。

## このフェーズで行うこと

1. **テストファイルの作成**
   - `tests/` ディレクトリに適切な名前でテストファイルを作成
   - 必要なインポートを追加
   - テストクラス・関数の骨組みを作成

2. **失敗するテストの作成**
   - 仕様を明確に定義するテストを書く
   - 期待する動作を assert で記述
   - エッジケースを考慮
   - エラーケースもテスト

3. **テストの実行と失敗確認**
   - `mise run test` を実行
   - テストが意図通り失敗することを確認
   - 失敗メッセージが適切であることを確認

## ベストプラクティス

- **明確な命名**: テスト名から何をテストしているか分かるようにする
- **1テスト1検証**: 1つのテストで1つのことだけを検証
- **AAA パターン**: Arrange（準備）, Act（実行）, Assert（検証）
- **Given-When-Then**: テストの意図を明確にする

## 例

```python
def test_workspace_initialization():
    """ワークスペース初期化が正しく動作する"""
    # Given: 新規ワークスペースパス
    ws_path = Path("/tmp/test_workspace")

    # When: ワークスペースを初期化
    workspace = Workspace(ws_path)
    workspace.initialize()

    # Then: 必要なディレクトリが作成される
    assert (ws_path / "config").exists()
    assert (ws_path / "ingest").exists()
    assert (ws_path / ".state").exists()
```

## 確認事項

- [ ] テストファイルが作成された
- [ ] テストが書かれた
- [ ] `mise run test` を実行した
- [ ] テストが失敗した（期待通り）
- [ ] 失敗メッセージが適切

## 次のステップ

テストが意図通り失敗したら、GREEN フェーズ（実装）に進みます。
