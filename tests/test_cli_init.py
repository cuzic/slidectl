"""
init コマンドのテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from typer.testing import CliRunner

from slidectl.cli import app

runner = CliRunner()


class TestInitCommand:
    """init コマンドのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_init_creates_workspace(self, temp_dir):
        """init コマンドがワークスペースを作成する"""
        ws_path = temp_dir / "test_ws"

        result = runner.invoke(app, ["init", "--ws", str(ws_path)])

        assert result.exit_code == 0
        assert "Workspace initialized successfully" in result.stdout

        # ディレクトリが作成される
        assert ws_path.exists()
        assert (ws_path / "config").exists()
        assert (ws_path / "ingest").exists()
        assert (ws_path / "instruct").exists()
        assert (ws_path / "build/assets/svg").exists()
        assert (ws_path / "render").exists()
        assert (ws_path / "optimize").exists()
        assert (ws_path / "report").exists()
        assert (ws_path / "out").exists()
        assert (ws_path / ".state").exists()
        assert (ws_path / ".logs").exists()

    def test_init_creates_config_files(self, temp_dir):
        """init コマンドが設定ファイルを作成する"""
        ws_path = temp_dir / "test_ws"

        result = runner.invoke(app, ["init", "--ws", str(ws_path)])

        assert result.exit_code == 0

        # 設定ファイルが作成される
        assert (ws_path / "config/layouts.yaml").exists()
        assert (ws_path / "config/policy.json").exists()

        # 設定ファイルの内容を確認
        layouts_content = (ws_path / "config/layouts.yaml").read_text()
        assert "text-only:" in layouts_content
        assert "max_lines: 18" in layouts_content

        policy_content = (ws_path / "config/policy.json").read_text()
        assert "density_range" in policy_content
        assert "max_iterations" in policy_content

    def test_init_fails_if_workspace_exists(self, temp_dir):
        """既存ワークスペースがある場合はエラー"""
        ws_path = temp_dir / "test_ws"

        # 1回目の初期化
        result1 = runner.invoke(app, ["init", "--ws", str(ws_path)])
        assert result1.exit_code == 0

        # 2回目の初期化（エラーになる）
        result2 = runner.invoke(app, ["init", "--ws", str(ws_path)])
        assert result2.exit_code == 2
        assert "already exists" in result2.stdout

    def test_init_with_force_overwrites(self, temp_dir):
        """--force オプションで再初期化できる"""
        ws_path = temp_dir / "test_ws"

        # 1回目の初期化
        result1 = runner.invoke(app, ["init", "--ws", str(ws_path)])
        assert result1.exit_code == 0

        # 設定ファイルを変更
        config_file = ws_path / "config/layouts.yaml"
        original_content = config_file.read_text()
        config_file.write_text("# modified")

        # --force で再初期化
        result2 = runner.invoke(app, ["init", "--ws", str(ws_path), "--force"])
        assert result2.exit_code == 0
        assert "Workspace initialized successfully" in result2.stdout

        # 設定ファイルが再生成されている
        new_content = config_file.read_text()
        assert new_content == original_content

    def test_init_default_workspace(self, temp_dir, monkeypatch):
        """デフォルトのワークスペースパス（./workspace）が使用される"""
        # 一時ディレクトリに移動
        monkeypatch.chdir(temp_dir)

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert (temp_dir / "workspace").exists()
        assert (temp_dir / "workspace/config").exists()
