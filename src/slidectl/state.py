"""
状態管理モジュール

実行状態の管理（run.json）とロック機構を提供します。
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RunState(BaseModel):
    """実行状態を管理するモデル"""

    version: str = Field(default="1.0", description="状態ファイルのバージョン")
    created_at: str = Field(description="作成日時（ISO 8601形式）")
    updated_at: str = Field(description="更新日時（ISO 8601形式）")
    steps: List[str] = Field(
        default_factory=lambda: [
            "ingest",
            "instruct",
            "build",
            "render",
            "measure",
            "optimize",
            "export",
        ],
        description="実行ステップのリスト",
    )
    last_ok: Optional[str] = Field(default=None, description="最後に成功したステップ")
    iteration: int = Field(default=0, description="反復カウント")
    lock: bool = Field(default=False, description="ロック状態")


class StateManager:
    """状態管理クラス

    ワークスペースの実行状態を管理します。

    Attributes:
        state_dir: 状態ディレクトリのパス
        run_file: run.json のパス
        lock_file: ロックファイルのパス

    Examples:
        >>> manager = StateManager(Path("workspace/.state"))
        >>> manager.initialize()
        >>> manager.lock()
        >>> manager.update_step("ingest")
        >>> manager.unlock()
    """

    def __init__(self, state_dir: Path):
        """状態管理を初期化

        Args:
            state_dir: 状態ディレクトリのパス
        """
        self.state_dir = state_dir
        self.run_file = state_dir / "run.json"
        self.lock_file = state_dir / "lock"

    def initialize(self) -> None:
        """状態を初期化

        新しい run.json を作成します。
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now().astimezone().isoformat()
        state = RunState(created_at=now, updated_at=now)

        self._save_state(state)

    def load(self) -> RunState:
        """状態を読み込む

        Returns:
            実行状態

        Raises:
            FileNotFoundError: run.json が存在しない場合
            ValueError: JSON形式が不正な場合
        """
        if not self.run_file.exists():
            raise FileNotFoundError(f"State file not found: {self.run_file}")

        try:
            with open(self.run_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return RunState(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in state file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading state: {e}")

    def save(self, state: RunState) -> None:
        """状態を保存

        Args:
            state: 実行状態
        """
        # updated_at を更新
        state.updated_at = datetime.now().astimezone().isoformat()
        self._save_state(state)

    def _save_state(self, state: RunState) -> None:
        """内部: 状態を保存

        Args:
            state: 実行状態
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)

        with open(self.run_file, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2, ensure_ascii=False)

    def is_locked(self) -> bool:
        """ロックされているか確認

        Returns:
            ロックされている場合True
        """
        if self.lock_file.exists():
            return True

        # run.json のロックフラグも確認
        try:
            state = self.load()
            return state.lock
        except (FileNotFoundError, ValueError):
            return False

    def lock(self) -> None:
        """ロックを取得

        Raises:
            RuntimeError: 既にロックされている場合
        """
        if self.is_locked():
            raise RuntimeError(
                f"Workspace is locked. Another process may be running. "
                f"If you're sure no other process is running, remove {self.lock_file}"
            )

        # state_dir を作成
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # ロックファイルを作成
        self.lock_file.touch()

        # run.json のロックフラグを更新
        try:
            state = self.load()
            state.lock = True
            self.save(state)
        except FileNotFoundError:
            # run.json が存在しない場合は初期化
            self.initialize()
            state = self.load()
            state.lock = True
            self.save(state)

    def unlock(self) -> None:
        """ロックを解除"""
        # ロックファイルを削除
        if self.lock_file.exists():
            self.lock_file.unlink()

        # run.json のロックフラグを更新
        try:
            state = self.load()
            state.lock = False
            self.save(state)
        except (FileNotFoundError, ValueError):
            pass  # ファイルが存在しない場合は無視

    def update_step(self, step: str) -> None:
        """ステップの進捗を記録

        Args:
            step: 完了したステップ名
        """
        state = self.load()
        state.last_ok = step
        self.save(state)

    def increment_iteration(self) -> int:
        """反復カウントをインクリメント

        Returns:
            新しい反復カウント
        """
        state = self.load()
        state.iteration += 1
        self.save(state)
        return state.iteration

    def reset_iteration(self) -> None:
        """反復カウントをリセット"""
        state = self.load()
        state.iteration = 0
        self.save(state)

    def get_iteration(self) -> int:
        """現在の反復カウントを取得

        Returns:
            反復カウント
        """
        state = self.load()
        return state.iteration

    def get_last_step(self) -> Optional[str]:
        """最後に成功したステップを取得

        Returns:
            最後に成功したステップ名（存在しない場合はNone）
        """
        try:
            state = self.load()
            return state.last_ok
        except (FileNotFoundError, ValueError):
            return None

    def exists(self) -> bool:
        """状態ファイルが存在するか確認

        Returns:
            状態ファイルが存在する場合True
        """
        return self.run_file.exists()
