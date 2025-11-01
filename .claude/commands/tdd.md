# TDD Development Cycle

このコマンドは、GitHub issueに対してTDD（Test-Driven Development）サイクルを実行します。

## 実行フロー

### Phase 1: PLAN 📋
1. 指定されたissueを読み込む
2. 関連ドキュメントを確認する
3. タスクリストを作成する
4. 実装計画を立てる（ファイル構成、インターフェース設計）

### Phase 2: RED 🔴（Test First）
1. テストファイルを作成する
2. 失敗するテストを書く（仕様を定義）
3. テストを実行して失敗を確認する（`mise run test`）
4. テストが意図通り失敗していることを確認する

### Phase 3: GREEN 🟢（Implementation）
1. テストをパスする最小限の実装を行う
2. テストを実行してパスを確認する（`mise run test`）
3. すべてのテストが通ることを確認する

### Phase 4: REFACTOR 🔧（Improvement）
1. コードを整理・改善する
   - 重複コードの削除
   - 関数・クラスの抽出
   - 命名の改善
   - 型ヒントの追加
2. テストを実行して、リファクタリング後も動作することを確認する
3. lintを実行する（`mise run lint`）

### Phase 5: VERIFY ✅（Quality Check）
1. すべてのテストを実行する（`mise run test`）
2. Linterを実行する（`mise run lint`）
3. 型チェックを実行する（mypy）
4. テストカバレッジを確認する
5. 必要に応じて追加のエッジケーステストを追加

### Phase 6: DOCUMENT 📝（Documentation）
1. コードにドキュメント文字列を追加する
2. 必要に応じてREADMEを更新する
3. コミットメッセージを作成する
4. GitHubにプッシュする
5. issueを更新する（進捗報告、完了時はclose）

## 使用方法

各フェーズを順次実行し、ユーザーに確認を取りながら進めます。

## ベストプラクティス

- **Small Steps**: 小さなステップで進める
- **Test First**: 必ずテストを先に書く
- **Refactor Fearlessly**: テストがあるので安心してリファクタリングできる
- **Commit Often**: 各フェーズでコミットする
- **Document Early**: 後回しにせず、実装と同時にドキュメントを書く

## 注意事項

- RED フェーズでは、テストが失敗することを確認する
- GREEN フェーズでは、最小限の実装のみ行う
- REFACTOR フェーズでは、機能追加せずコードの改善のみ行う
- 各フェーズで必ずテストを実行する
