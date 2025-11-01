"""
slidectl CLI エントリーポイント

Typerベースのコマンドラインインターフェース
"""

import typer
from rich import print as rprint
from pathlib import Path
import shutil

from slidectl.workspace import Workspace
from slidectl.config import Config
from slidectl.ingest import MarkdownIngestor
from slidectl.logger import Logger

app = typer.Typer(
    name="slidectl",
    help="非LLMスライド生成オーケストレータ - Markdown原稿からMarpスライドを自動生成・最適化",
    no_args_is_help=True,
)


@app.command()
def init(
    ws: Path = typer.Option(
        Path("./workspace"),
        "--ws",
        help="ワークスペースディレクトリ",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="既存ファイルを上書き",
    ),
):
    """設定・ワークスペースを初期化"""
    workspace = Workspace(ws)

    try:
        rprint(f"[blue]📁 Initializing workspace at: {ws}[/blue]")

        # ワークスペースを初期化
        workspace.initialize(force=force)

        # デフォルト設定ファイルをコピー
        config_dir = workspace.get_config_dir()

        # プロジェクトルートの config/ からコピー
        project_root = Path(__file__).parent.parent.parent
        default_config_dir = project_root / "config"

        if default_config_dir.exists():
            # layouts.yaml をコピー
            layouts_src = default_config_dir / "layouts.yaml"
            if layouts_src.exists():
                shutil.copy(layouts_src, config_dir / "layouts.yaml")

            # policy.json をコピー
            policy_src = default_config_dir / "policy.json"
            if policy_src.exists():
                shutil.copy(policy_src, config_dir / "policy.json")
        else:
            # デフォルト設定をコード内から生成
            (config_dir / "layouts.yaml").write_text(Config.get_default_layouts_yaml())
            (config_dir / "policy.json").write_text(Config.get_default_policy_json())

        rprint("[green]✅ Workspace initialized successfully![/green]")
        rprint("\n[dim]Created directories:[/dim]")
        rprint("  • config/")
        rprint("  • ingest/")
        rprint("  • instruct/")
        rprint("  • build/assets/svg/")
        rprint("  • render/")
        rprint("  • optimize/")
        rprint("  • report/")
        rprint("  • out/")
        rprint("  • .state/")
        rprint("  • .logs/")

        rprint("\n[dim]Configuration files:[/dim]")
        rprint("  • config/layouts.yaml")
        rprint("  • config/policy.json")

    except FileExistsError:
        rprint(f"[red]❌ Error: Workspace already exists at {ws}[/red]")
        rprint("[yellow]💡 Use --force to overwrite existing workspace[/yellow]")
        raise typer.Exit(2)
    except Exception as e:
        rprint(f"[red]❌ Error initializing workspace: {e}[/red]")
        raise typer.Exit(2)


@app.command()
def ingest(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    input_file: Path = typer.Option(..., "--in", help="入力Markdownファイル"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力"),
):
    """Markdown正規化・構造解析"""
    workspace = Workspace(ws)
    logger = Logger(workspace.get_logs_dir(), step="ingest", json_mode=json_output)

    try:
        # ワークスペースの存在確認
        if not workspace.exists():
            rprint(f"[red]❌ Error: Workspace not found at {ws}[/red]")
            rprint("[yellow]💡 Run 'slidectl init' first to create workspace[/yellow]")
            raise typer.Exit(2)

        # 入力ファイルの存在確認
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            rprint(f"[red]❌ Error: Input file not found: {input_file}[/red]")
            raise typer.Exit(2)

        logger.info(f"Starting ingest process for: {input_file}")
        rprint(f"[blue]📄 Processing Markdown file: {input_file}[/blue]")

        # Markdown処理
        ingestor = MarkdownIngestor()
        normalized, structure = ingestor.process(input_file)

        # 出力ファイルを保存
        output_dir = workspace.get_ingest_dir()
        normalized_path, structure_path = ingestor.save_outputs(output_dir, normalized, structure)

        logger.info(
            "Ingest completed",
            sections=len(structure.sections),
            slides_hint=sum(len(s.slides_hint) for s in structure.sections),
        )

        rprint("[green]✅ Ingest completed successfully![/green]")
        rprint("\n[dim]Outputs:[/dim]")
        rprint(f"  • {normalized_path}")
        rprint(f"  • {structure_path}")
        rprint("\n[dim]Structure:[/dim]")
        rprint(f"  • Document: {structure.doc_title}")
        rprint(f"  • Sections: {len(structure.sections)}")
        total_hints = sum(len(s.slides_hint) for s in structure.sections)
        rprint(f"  • Slide hints: {total_hints}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        rprint(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(2)
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        rprint(f"[red]❌ Error during ingest: {e}[/red]")
        raise typer.Exit(2)


@app.command()
def instruct(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """LLMに指示JSON生成を依頼"""
    rprint("[yellow]🚧 instruct コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def build(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """LLMにMarp.md + SVG生成を依頼"""
    rprint("[yellow]🚧 build コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def render(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """marp-cliでHTML/PPTX生成"""
    rprint("[yellow]🚧 render コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def measure(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """PlaywrightでDOM計測"""
    rprint("[yellow]🚧 measure コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def optimize(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    max_iter: int = typer.Option(3, "--max-iter", help="最大反復回数"),
):
    """スコア判定→再生成反復"""
    rprint("[yellow]🚧 optimize コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def export(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    pptx_name: str = typer.Option(
        "presentation_final.pptx", "--pptx-name", help="出力PPTXファイル名"
    ),
):
    """PPTX出力"""
    rprint("[yellow]🚧 export コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def status(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力"),
):
    """処理状態確認"""
    rprint("[yellow]🚧 status コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


def version_callback(value: bool):
    if value:
        from slidectl import __version__

        rprint(f"slidectl version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="バージョン表示",
    ),
):
    """
    slidectl - 非LLMスライド生成オーケストレータ
    """
    pass


if __name__ == "__main__":
    app()
