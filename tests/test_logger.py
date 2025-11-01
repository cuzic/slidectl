"""
ロギング機能のテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import sys
from io import StringIO

from slidectl.logger import Logger, LogLevel


class TestLogLevel:
    """LogLevelのテスト"""

    def test_log_level_values(self):
        """ログレベルの値が正しい"""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"


class TestLogger:
    """Loggerクラスのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def logger(self, temp_dir):
        """Loggerインスタンスを作成"""
        log_dir = temp_dir / ".logs"
        return Logger(log_dir, step="test")

    @pytest.fixture
    def logger_no_step(self, temp_dir):
        """ステップなしのLoggerインスタンスを作成"""
        log_dir = temp_dir / ".logs"
        return Logger(log_dir)

    def test_logger_initialization(self, logger, temp_dir):
        """ロガーの初期化が正しく動作する"""
        log_dir = temp_dir / ".logs"
        assert logger.log_dir == log_dir
        assert logger.step == "test"
        assert logger.json_mode is False

        # ログディレクトリが作成される
        assert log_dir.exists()
        assert log_dir.is_dir()

        # ログファイルのパスが正しい
        assert logger.log_file == log_dir / "test.jsonl"

    def test_logger_without_step(self, logger_no_step, temp_dir):
        """ステップなしのロガーの初期化"""
        log_dir = temp_dir / ".logs"
        assert logger_no_step.log_file == log_dir / "slidectl.jsonl"

    def test_info_writes_to_file(self, logger):
        """INFOログがファイルに書き込まれる"""
        logger.info("Test message")

        # ログファイルが作成される
        assert logger.log_file.exists()

        # ログファイルの内容を確認
        with open(logger.log_file, "r", encoding="utf-8") as f:
            line = f.readline()
            data = json.loads(line)

        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["step"] == "test"
        assert "timestamp" in data

    def test_debug_log(self, logger):
        """DEBUGログが正しく出力される"""
        logger.debug("Debug message")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["level"] == "DEBUG"
        assert data["message"] == "Debug message"

    def test_warning_log(self, logger):
        """WARNINGログが正しく出力される"""
        logger.warning("Warning message")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["level"] == "WARNING"
        assert data["message"] == "Warning message"

    def test_error_log(self, logger):
        """ERRORログが正しく出力される"""
        logger.error("Error message")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["level"] == "ERROR"
        assert data["message"] == "Error message"

    def test_log_with_extra_fields(self, logger):
        """追加フィールド付きログが正しく出力される"""
        logger.info("Message", file_count=10, status="ok")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["message"] == "Message"
        assert data["file_count"] == 10
        assert data["status"] == "ok"

    def test_multiple_log_entries(self, logger):
        """複数のログエントリが正しく記録される"""
        logger.info("First")
        logger.warning("Second")
        logger.error("Third")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 3

        data1 = json.loads(lines[0])
        assert data1["level"] == "INFO"
        assert data1["message"] == "First"

        data2 = json.loads(lines[1])
        assert data2["level"] == "WARNING"
        assert data2["message"] == "Second"

        data3 = json.loads(lines[2])
        assert data3["level"] == "ERROR"
        assert data3["message"] == "Third"

    def test_log_without_step(self, logger_no_step):
        """ステップなしのログが正しく出力される"""
        logger_no_step.info("No step message")

        with open(logger_no_step.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["message"] == "No step message"
        assert "step" not in data

    def test_get_log_file(self, logger):
        """ログファイルのパスを取得できる"""
        log_file = logger.get_log_file()
        assert log_file == logger.log_file
        assert log_file.name == "test.jsonl"

    def test_json_mode_initialization(self, temp_dir):
        """JSONモードでの初期化が正しく動作する"""
        log_dir = temp_dir / ".logs"
        logger = Logger(log_dir, step="test", json_mode=True)

        assert logger.json_mode is True

    def test_json_mode_output(self, temp_dir, capsys):
        """JSONモードでの出力が正しい"""
        log_dir = temp_dir / ".logs"
        logger = Logger(log_dir, step="test", json_mode=True)

        logger.info("JSON mode message")

        # stdout に JSON が出力される
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())

        assert output["level"] == "INFO"
        assert output["message"] == "JSON mode message"
        assert output["step"] == "test"
        assert "timestamp" in output

    def test_unicode_message(self, logger):
        """Unicodeメッセージが正しく処理される"""
        logger.info("日本語メッセージ")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["message"] == "日本語メッセージ"

    def test_timestamp_format(self, logger):
        """タイムスタンプが ISO 8601 形式である"""
        logger.info("Test")

        with open(logger.log_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        # ISO 8601 形式のチェック（簡易）
        timestamp = data["timestamp"]
        assert "T" in timestamp
        # タイムゾーンオフセットがある（+, -, または Z）
        assert "+" in timestamp or "-" in timestamp.split("T")[1] or "Z" in timestamp
