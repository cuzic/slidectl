"""
ワークスペース管理のテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from slidectl.workspace import Workspace, WorkspaceStructure


class TestWorkspace:
    """Workspaceクラスのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_workspace_initialization(self, temp_dir):
        """ワークスペースの初期化が正しく動作する"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        # 初期化前は存在しない
        assert not ws.exists()

        # 初期化
        ws.initialize()

        # 初期化後は存在する
        assert ws.exists()

        # すべてのディレクトリが作成されている
        assert ws.structure.config.exists()
        assert ws.structure.ingest.exists()
        assert ws.structure.instruct.exists()
        assert ws.structure.build.exists()
        assert ws.structure.build_assets_svg.exists()
        assert ws.structure.render.exists()
        assert ws.structure.optimize.exists()
        assert ws.structure.report.exists()
        assert ws.structure.out.exists()
        assert ws.structure.state.exists()
        assert ws.structure.logs.exists()

    def test_workspace_exists_when_not_initialized(self, temp_dir):
        """初期化されていないワークスペースは存在しない"""
        ws_path = temp_dir / "nonexistent"
        ws = Workspace(ws_path)

        assert not ws.exists()

    def test_workspace_validate_when_complete(self, temp_dir):
        """完全なワークスペースは検証をパスする"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)
        ws.initialize()

        assert ws.validate()

    def test_workspace_validate_when_incomplete(self, temp_dir):
        """不完全なワークスペースは検証に失敗する"""
        ws_path = temp_dir / "incomplete_workspace"
        ws = Workspace(ws_path)

        # ルートだけ作成
        ws_path.mkdir()

        # 検証は失敗
        assert not ws.validate()

    def test_workspace_initialize_raises_when_exists(self, temp_dir):
        """既存のワークスペースに対してforce=Falseで初期化するとエラー"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        # 初回の初期化
        ws.initialize()

        # 2回目の初期化（force=False）はエラー
        with pytest.raises(FileExistsError):
            ws.initialize(force=False)

    def test_workspace_initialize_with_force(self, temp_dir):
        """force=Trueで既存のワークスペースを上書きできる"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        # 初回の初期化
        ws.initialize()

        # force=Trueで再初期化（エラーなし）
        ws.initialize(force=True)

        assert ws.exists()
        assert ws.validate()

    def test_resolve_path_within_workspace(self, temp_dir):
        """ワークスペース内のパスが正しく解決される"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        resolved = ws.resolve_path("config/layouts.yaml")

        assert resolved == ws_path / "config" / "layouts.yaml"
        assert resolved.is_relative_to(ws_path)

    def test_resolve_path_outside_workspace_raises(self, temp_dir):
        """ワークスペース外のパスはエラー"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        with pytest.raises(ValueError, match="outside workspace"):
            ws.resolve_path("../outside/file.txt")

    def test_get_directory_methods(self, temp_dir):
        """各ディレクトリ取得メソッドが正しく動作する"""
        ws_path = temp_dir / "test_workspace"
        ws = Workspace(ws_path)

        assert ws.get_config_dir() == ws_path / "config"
        assert ws.get_ingest_dir() == ws_path / "ingest"
        assert ws.get_instruct_dir() == ws_path / "instruct"
        assert ws.get_build_dir() == ws_path / "build"
        assert ws.get_build_assets_svg_dir() == ws_path / "build" / "assets" / "svg"
        assert ws.get_render_dir() == ws_path / "render"
        assert ws.get_optimize_dir() == ws_path / "optimize"
        assert ws.get_report_dir() == ws_path / "report"
        assert ws.get_out_dir() == ws_path / "out"
        assert ws.get_state_dir() == ws_path / ".state"
        assert ws.get_logs_dir() == ws_path / ".logs"
