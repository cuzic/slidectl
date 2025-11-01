# REFACTOR Phase - コード改善

TDDサイクルの REFACTOR フェーズ：テストを維持しながらコードを改善します。

## このフェーズで行うこと

1. **コードの整理**
   - 重複コードの削除（DRY原則）
   - 長い関数の分割
   - マジックナンバーの定数化
   - 複雑な条件式の簡素化

2. **品質向上**
   - 命名の改善（変数名、関数名、クラス名）
   - 型ヒントの追加・改善
   - ドキュメント文字列の追加
   - コメントの追加（必要な箇所のみ）

3. **設計の改善**
   - 関数・クラスの抽出
   - 責任の分離（Single Responsibility Principle）
   - 依存関係の整理
   - インターフェースの明確化

4. **継続的な検証**
   - リファクタリング後に毎回テストを実行
   - すべてのテストがパスすることを確認
   - Linterを実行してスタイルをチェック

## リファクタリングパターン

### 関数の抽出
```python
# Before
def process_data(data):
    # 複雑な処理
    result = []
    for item in data:
        if item["type"] == "A":
            # 長い処理
            ...
    return result

# After
def process_data(data):
    return [process_type_a(item) for item in data if is_type_a(item)]

def is_type_a(item):
    return item["type"] == "A"

def process_type_a(item):
    # 処理を抽出
    ...
```

### マジックナンバーの定数化
```python
# Before
if density > 0.018:
    ...

# After
MAX_DENSITY = 0.018

if density > MAX_DENSITY:
    ...
```

### 型ヒントの追加
```python
# Before
def calculate_density(area, slide_area):
    return area / slide_area

# After
def calculate_density(area: float, slide_area: float) -> float:
    """文字密度を計算する"""
    return area / slide_area
```

## 確認事項

- [ ] コードを整理・改善した
- [ ] 命名を改善した
- [ ] 型ヒントを追加した
- [ ] ドキュメント文字列を追加した
- [ ] `mise run test` を実行した
- [ ] すべてのテストがパスした
- [ ] `mise run lint` を実行した
- [ ] Lintエラーがない

## 注意事項

⚠️ **リファクタリング時は新機能を追加しない**
- 既存の動作を変えずにコードを改善する
- 新機能は次のサイクルで追加する
- テストが通り続けることを常に確認する

## 次のステップ

リファクタリングが完了したら、VERIFY フェーズ（品質確認）に進みます。
