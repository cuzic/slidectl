"""
ワークスペース管理モジュール

ワークスペースディレクトリの構造定義、初期化、検証機能を提供します。
"""

from pathlib import Path
from pydantic import BaseModel, Field


class WorkspaceStructure(BaseModel):
    """ワークスペースのディレクトリ構造を定義するモデル"""

    root: Path = Field(description="ワークスペースのルートディレクトリ")
    config: Path = Field(description="設定ファイル")
    ingest: Path = Field(description="原稿正規化・構造")
    instruct: Path = Field(description="スライド設計（LLM出力）")
    build: Path = Field(description="Marp.md と資材")
    build_assets_svg: Path = Field(description="SVG資材")
    render: Path = Field(description="中間レンダリング")
    optimize: Path = Field(description="計測・パッチ")
    report: Path = Field(description="CSV等")
    out: Path = Field(description="最終物")
    state: Path = Field(description="実行ロック・実行履歴")
    logs: Path = Field(description="実行ログ(JSONL)")


class Workspace:
    """ワークスペース管理クラス

    ワークスペースの初期化、検証、パス解決などの機能を提供します。

    Attributes:
        root: ワークスペースのルートディレクトリパス
        structure: ワークスペースのディレクトリ構造

    Examples:
        >>> ws = Workspace(Path("./workspace"))
        >>> ws.initialize()
        >>> ws.exists()
        True
    """

    def __init__(self, root: Path):
        """ワークスペースを初期化

        Args:
            root: ワークスペースのルートディレクトリパス
        """
        self.root = root.resolve()
        self.structure = self._build_structure()

    def _build_structure(self) -> WorkspaceStructure:
        """ワークスペース構造を構築

        Returns:
            ワークスペースのディレクトリ構造
        """
        return WorkspaceStructure(
            root=self.root,
            config=self.root / "config",
            ingest=self.root / "ingest",
            instruct=self.root / "instruct",
            build=self.root / "build",
            build_assets_svg=self.root / "build" / "assets" / "svg",
            render=self.root / "render",
            optimize=self.root / "optimize",
            report=self.root / "report",
            out=self.root / "out",
            state=self.root / ".state",
            logs=self.root / ".logs",
        )

    def initialize(self, force: bool = False) -> None:
        """ワークスペースを初期化してディレクトリを作成

        Args:
            force: Trueの場合、既存ディレクトリを上書き

        Raises:
            FileExistsError: ワークスペースが既に存在し、forceがFalseの場合
        """
        if self.exists() and not force:
            raise FileExistsError(
                f"Workspace already exists at {self.root}. " f"Use force=True to overwrite."
            )

        # ルートディレクトリを作成
        self.root.mkdir(parents=True, exist_ok=True)

        # 各ディレクトリを作成
        directories = [
            self.structure.config,
            self.structure.ingest,
            self.structure.instruct,
            self.structure.build,
            self.structure.build_assets_svg,
            self.structure.render,
            self.structure.optimize,
            self.structure.report,
            self.structure.out,
            self.structure.state,
            self.structure.logs,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        """ワークスペースが存在するか確認

        Returns:
            ワークスペースのルートディレクトリが存在する場合True
        """
        return self.root.exists() and self.root.is_dir()

    def validate(self) -> bool:
        """ワークスペースの構造を検証

        必要なすべてのディレクトリが存在するか確認します。

        Returns:
            すべての必須ディレクトリが存在する場合True
        """
        if not self.exists():
            return False

        required_directories = [
            self.structure.config,
            self.structure.ingest,
            self.structure.instruct,
            self.structure.build,
            self.structure.build_assets_svg,
            self.structure.render,
            self.structure.optimize,
            self.structure.report,
            self.structure.out,
            self.structure.state,
            self.structure.logs,
        ]

        return all(d.exists() and d.is_dir() for d in required_directories)

    def resolve_path(self, relative_path: str) -> Path:
        """ワークスペース相対パスを絶対パスに解決

        Args:
            relative_path: ワークスペース相対のパス文字列

        Returns:
            解決された絶対パス

        Raises:
            ValueError: パスがワークスペース外を指している場合

        Examples:
            >>> ws = Workspace(Path("/workspace"))
            >>> ws.resolve_path("config/layouts.yaml")
            Path('/workspace/config/layouts.yaml')
        """
        resolved = (self.root / relative_path).resolve()

        # ワークスペース内のパスであることを確認
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise ValueError(f"Path '{relative_path}' resolves outside workspace: {resolved}")

        return resolved

    def get_config_dir(self) -> Path:
        """設定ディレクトリのパスを取得"""
        return self.structure.config

    def get_ingest_dir(self) -> Path:
        """ingestディレクトリのパスを取得"""
        return self.structure.ingest

    def get_instruct_dir(self) -> Path:
        """instructディレクトリのパスを取得"""
        return self.structure.instruct

    def get_build_dir(self) -> Path:
        """buildディレクトリのパスを取得"""
        return self.structure.build

    def get_build_assets_svg_dir(self) -> Path:
        """build/assets/svgディレクトリのパスを取得"""
        return self.structure.build_assets_svg

    def get_render_dir(self) -> Path:
        """renderディレクトリのパスを取得"""
        return self.structure.render

    def get_optimize_dir(self) -> Path:
        """optimizeディレクトリのパスを取得"""
        return self.structure.optimize

    def get_report_dir(self) -> Path:
        """reportディレクトリのパスを取得"""
        return self.structure.report

    def get_out_dir(self) -> Path:
        """outディレクトリのパスを取得"""
        return self.structure.out

    def get_state_dir(self) -> Path:
        """stateディレクトリのパスを取得"""
        return self.structure.state

    def get_logs_dir(self) -> Path:
        """logsディレクトリのパスを取得"""
        return self.structure.logs
