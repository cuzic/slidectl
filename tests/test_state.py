"""
状態管理のテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import time

from slidectl.state import StateManager, RunState


class TestRunState:
    """RunStateモデルのテスト"""

    def test_default_run_state(self):
        """デフォルトの状態が正しい"""
        state = RunState(
            created_at="2025-11-01T10:00:00+09:00",
            updated_at="2025-11-01T10:00:00+09:00",
        )

        assert state.version == "1.0"
        assert state.steps == [
            "ingest",
            "instruct",
            "build",
            "render",
            "measure",
            "optimize",
            "export",
        ]
        assert state.last_ok is None
        assert state.iteration == 0
        assert state.lock is False


class TestStateManager:
    """StateManagerクラスのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def state_manager(self, temp_dir):
        """StateManagerインスタンスを作成"""
        state_dir = temp_dir / ".state"
        return StateManager(state_dir)

    def test_initialize(self, state_manager):
        """状態の初期化が正しく動作する"""
        state_manager.initialize()

        # ファイルが作成される
        assert state_manager.run_file.exists()

        # 状態を読み込める
        state = state_manager.load()
        assert state.version == "1.0"
        assert state.created_at is not None
        assert state.updated_at is not None
        assert state.last_ok is None
        assert state.iteration == 0
        assert state.lock is False

    def test_load_nonexistent_file(self, state_manager):
        """存在しないファイルの読み込みはエラー"""
        with pytest.raises(FileNotFoundError):
            state_manager.load()

    def test_save_and_load(self, state_manager):
        """状態の保存と読み込みが正しく動作する"""
        state_manager.initialize()

        # 状態を変更して保存
        state = state_manager.load()
        state.last_ok = "ingest"
        state.iteration = 5
        state_manager.save(state)

        # 読み込んで確認
        loaded_state = state_manager.load()
        assert loaded_state.last_ok == "ingest"
        assert loaded_state.iteration == 5

    def test_lock_and_unlock(self, state_manager):
        """ロックと解除が正しく動作する"""
        state_manager.initialize()

        # 初期状態はロックされていない
        assert not state_manager.is_locked()

        # ロックを取得
        state_manager.lock()
        assert state_manager.is_locked()
        assert state_manager.lock_file.exists()

        # run.json のロックフラグも確認
        state = state_manager.load()
        assert state.lock is True

        # ロックを解除
        state_manager.unlock()
        assert not state_manager.is_locked()
        assert not state_manager.lock_file.exists()

        # run.json のロックフラグも確認
        state = state_manager.load()
        assert state.lock is False

    def test_lock_when_already_locked(self, state_manager):
        """既にロックされている場合はエラー"""
        state_manager.initialize()
        state_manager.lock()

        # 2回目のロックはエラー
        with pytest.raises(RuntimeError, match="locked"):
            state_manager.lock()

    def test_lock_without_initialize(self, state_manager):
        """初期化前でもロックを取得できる"""
        # 初期化なしでロック
        state_manager.lock()

        assert state_manager.is_locked()
        assert state_manager.exists()

    def test_update_step(self, state_manager):
        """ステップ進捗の記録が正しく動作する"""
        state_manager.initialize()

        # ステップを更新
        state_manager.update_step("ingest")
        assert state_manager.load().last_ok == "ingest"

        state_manager.update_step("build")
        assert state_manager.load().last_ok == "build"

    def test_increment_iteration(self, state_manager):
        """反復カウントのインクリメントが正しく動作する"""
        state_manager.initialize()

        assert state_manager.get_iteration() == 0

        # インクリメント
        count = state_manager.increment_iteration()
        assert count == 1
        assert state_manager.get_iteration() == 1

        count = state_manager.increment_iteration()
        assert count == 2
        assert state_manager.get_iteration() == 2

    def test_reset_iteration(self, state_manager):
        """反復カウントのリセットが正しく動作する"""
        state_manager.initialize()

        # カウントを増やす
        state_manager.increment_iteration()
        state_manager.increment_iteration()
        assert state_manager.get_iteration() == 2

        # リセット
        state_manager.reset_iteration()
        assert state_manager.get_iteration() == 0

    def test_get_last_step_when_not_exists(self, state_manager):
        """状態ファイルが存在しない場合はNoneを返す"""
        assert state_manager.get_last_step() is None

    def test_get_last_step(self, state_manager):
        """最後に成功したステップを取得できる"""
        state_manager.initialize()
        state_manager.update_step("render")

        assert state_manager.get_last_step() == "render"

    def test_exists(self, state_manager):
        """状態ファイルの存在確認が正しく動作する"""
        assert not state_manager.exists()

        state_manager.initialize()
        assert state_manager.exists()

    def test_load_invalid_json(self, state_manager, temp_dir):
        """不正なJSONはエラー"""
        state_dir = temp_dir / ".state"
        state_dir.mkdir()

        # 不正なJSONを書き込む
        run_file = state_dir / "run.json"
        run_file.write_text("{invalid json}")

        with pytest.raises(ValueError, match="Invalid JSON"):
            state_manager.load()

    def test_updated_at_changes(self, state_manager):
        """saveするとupdated_atが更新される"""
        state_manager.initialize()

        state1 = state_manager.load()
        updated_at_1 = state1.updated_at

        # 少し待つ
        time.sleep(0.01)

        # 保存
        state1.last_ok = "test"
        state_manager.save(state1)

        state2 = state_manager.load()
        updated_at_2 = state2.updated_at

        # updated_at が変わっている
        assert updated_at_2 > updated_at_1
