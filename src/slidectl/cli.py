"""
slidectl CLI エントリーポイント

Typerベースのコマンドラインインターフェース
"""

import typer
from rich import print as rprint
from pathlib import Path

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
    rprint(f"[yellow]🚧 init コマンドは未実装です[/yellow]")
    rprint(f"[dim]ワークスペース: {ws}[/dim]")
    raise typer.Exit(1)


@app.command()
def ingest(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    input_file: Path = typer.Option(..., "--in", help="入力Markdownファイル"),
):
    """Markdown正規化・構造解析"""
    rprint(f"[yellow]🚧 ingest コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def instruct(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """LLMに指示JSON生成を依頼"""
    rprint(f"[yellow]🚧 instruct コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def build(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """LLMにMarp.md + SVG生成を依頼"""
    rprint(f"[yellow]🚧 build コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def render(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """marp-cliでHTML/PPTX生成"""
    rprint(f"[yellow]🚧 render コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def measure(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
):
    """PlaywrightでDOM計測"""
    rprint(f"[yellow]🚧 measure コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def optimize(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    max_iter: int = typer.Option(3, "--max-iter", help="最大反復回数"),
):
    """スコア判定→再生成反復"""
    rprint(f"[yellow]🚧 optimize コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def export(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    pptx_name: str = typer.Option("presentation_final.pptx", "--pptx-name", help="出力PPTXファイル名"),
):
    """PPTX出力"""
    rprint(f"[yellow]🚧 export コマンドは未実装です[/yellow]")
    raise typer.Exit(1)


@app.command()
def status(
    ws: Path = typer.Option(Path("./workspace"), "--ws", help="ワークスペースディレクトリ"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力"),
):
    """処理状態確認"""
    rprint(f"[yellow]🚧 status コマンドは未実装です[/yellow]")
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
