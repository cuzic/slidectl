"""
ロギング基盤モジュール

JSON Lines形式のログ出力と、richによる人間可読ログを提供します。
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum

from rich.console import Console


class LogLevel(str, Enum):
    """ログレベル"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    """ロガークラス

    JSON Lines形式のログファイル出力と、richによるコンソール出力を提供します。

    Attributes:
        log_dir: ログディレクトリのパス
        step: 現在のステップ名
        json_mode: JSON出力モード（機械可読）

    Examples:
        >>> logger = Logger(Path("workspace/.logs"), step="ingest")
        >>> logger.info("Processing file")
        >>> logger.error("Failed to process")
    """

    def __init__(
        self,
        log_dir: Path,
        step: Optional[str] = None,
        json_mode: bool = False,
    ):
        """ロガーを初期化

        Args:
            log_dir: ログディレクトリのパス
            step: ステップ名（Noneの場合は共通ログ）
            json_mode: JSON出力モード
        """
        self.log_dir = log_dir
        self.step = step
        self.json_mode = json_mode

        # ログディレクトリを作成
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # ログファイルのパス
        if step:
            self.log_file = log_dir / f"{step}.jsonl"
        else:
            self.log_file = log_dir / "slidectl.jsonl"

        # Richコンソールを初期化
        if json_mode:
            # JSON モードでは stderr に出力
            self.console = Console(stderr=True, force_terminal=False)
        else:
            # 通常モードでは stderr に Rich 出力
            self.console = Console(stderr=True)

    def _write_log_file(self, level: LogLevel, message: str, extra: Optional[dict] = None) -> None:
        """ログファイルに JSON Lines 形式で書き込む

        Args:
            level: ログレベル
            message: ログメッセージ
            extra: 追加情報
        """
        log_entry = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "level": level.value,
            "message": message,
        }

        if self.step:
            log_entry["step"] = self.step

        if extra:
            log_entry.update(extra)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def _output_console(self, level: LogLevel, message: str) -> None:
        """コンソールに出力

        Args:
            level: ログレベル
            message: ログメッセージ
        """
        if self.json_mode:
            # JSON モード: stdout に JSON Lines 出力
            output = {
                "timestamp": datetime.now().astimezone().isoformat(),
                "level": level.value,
                "message": message,
            }
            if self.step:
                output["step"] = self.step
            print(json.dumps(output, ensure_ascii=False), file=sys.stdout)
        else:
            # 通常モード: Rich による見やすい出力
            timestamp = datetime.now().strftime("%H:%M:%S")
            if level == LogLevel.DEBUG:
                self.console.print(f"[dim][{timestamp}] DEBUG    {message}[/dim]")
            elif level == LogLevel.INFO:
                self.console.print(f"[{timestamp}] INFO     {message}")
            elif level == LogLevel.WARNING:
                self.console.print(f"[yellow][{timestamp}] WARNING  {message}[/yellow]")
            elif level == LogLevel.ERROR:
                self.console.print(f"[red][{timestamp}] ERROR    {message}[/red]")

    def debug(self, message: str, **extra) -> None:
        """DEBUGレベルのログを出力

        Args:
            message: ログメッセージ
            **extra: 追加情報
        """
        self._write_log_file(LogLevel.DEBUG, message, extra)
        self._output_console(LogLevel.DEBUG, message)

    def info(self, message: str, **extra) -> None:
        """INFOレベルのログを出力

        Args:
            message: ログメッセージ
            **extra: 追加情報
        """
        self._write_log_file(LogLevel.INFO, message, extra)
        self._output_console(LogLevel.INFO, message)

    def warning(self, message: str, **extra) -> None:
        """WARNINGレベルのログを出力

        Args:
            message: ログメッセージ
            **extra: 追加情報
        """
        self._write_log_file(LogLevel.WARNING, message, extra)
        self._output_console(LogLevel.WARNING, message)

    def error(self, message: str, **extra) -> None:
        """ERRORレベルのログを出力

        Args:
            message: ログメッセージ
            **extra: 追加情報
        """
        self._write_log_file(LogLevel.ERROR, message, extra)
        self._output_console(LogLevel.ERROR, message)

    def get_log_file(self) -> Path:
        """ログファイルのパスを取得

        Returns:
            ログファイルのパス
        """
        return self.log_file
