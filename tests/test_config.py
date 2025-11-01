"""
設定ファイル管理のテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import yaml

from slidectl.config import (
    Config,
    LayoutsConfig,
    PolicyConfig,
    TextOnlyLayout,
    TwoColumnLayout,
    ImageRightLayout,
    QuoteSlideLayout,
    CommandsConfig,
)


class TestLayoutsConfig:
    """LayoutsConfigのテスト"""

    def test_default_layouts(self):
        """デフォルトのレイアウト設定が正しい"""
        layouts = LayoutsConfig()

        assert layouts.text_only.max_lines == 18
        assert layouts.text_only.prefer_assets == False
        assert layouts.two_column.left_max_lines == 10
        assert layouts.two_column.right_max_lines == 10
        assert layouts.image_right.text_max_lines == 12
        assert layouts.image_right.image_width_pct == 40
        assert layouts.quote_slide.max_lines == 6


class TestPolicyConfig:
    """PolicyConfigのテスト"""

    def test_default_policy(self):
        """デフォルトのポリシー設定が正しい"""
        policy = PolicyConfig()

        assert policy.density_range == (0.012, 0.018)
        assert policy.whitespace_range == (0.15, 0.40)
        assert policy.max_iterations == 3
        assert "LLM CLI not configured" in policy.commands.instruct_cmd

    def test_validate_density_range(self):
        """density_rangeのバリデーション"""
        # 正常ケース
        policy = PolicyConfig(density_range=(0.01, 0.02))
        assert policy.density_range == (0.01, 0.02)

        # 逆転（エラー）
        with pytest.raises(ValueError, match="min must be less than max"):
            PolicyConfig(density_range=(0.02, 0.01))

        # 範囲外（エラー）
        with pytest.raises(ValueError, match="between 0 and 1"):
            PolicyConfig(density_range=(-0.1, 0.5))

    def test_validate_whitespace_range(self):
        """whitespace_rangeのバリデーション"""
        # 正常ケース
        policy = PolicyConfig(whitespace_range=(0.1, 0.5))
        assert policy.whitespace_range == (0.1, 0.5)

        # 逆転（エラー）
        with pytest.raises(ValueError, match="min must be less than max"):
            PolicyConfig(whitespace_range=(0.5, 0.1))

    def test_validate_max_iterations(self):
        """max_iterationsのバリデーション"""
        # 正常ケース
        policy = PolicyConfig(max_iterations=5)
        assert policy.max_iterations == 5

        # 0以下（エラー）
        with pytest.raises(ValueError, match="must be at least 1"):
            PolicyConfig(max_iterations=0)


class TestConfig:
    """Configクラスのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_load_from_dir_with_files(self, temp_dir):
        """設定ファイルが存在する場合の読み込み"""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        # layouts.yaml を作成
        layouts_yaml = config_dir / "layouts.yaml"
        layouts_yaml.write_text(
            """layouts:
  text-only:
    max_lines: 20
    prefer_assets: true
  two-column:
    left_max_lines: 15
    right_max_lines: 15
  image-right:
    text_max_lines: 10
    image_width_pct: 50
  quote-slide:
    max_lines: 8
"""
        )

        # policy.json を作成
        policy_json = config_dir / "policy.json"
        policy_json.write_text(
            json.dumps(
                {
                    "density_range": [0.01, 0.02],
                    "whitespace_range": [0.2, 0.5],
                    "max_iterations": 5,
                    "commands": {
                        "instruct_cmd": "custom instruct",
                        "build_cmd": "custom build",
                        "augment_cmd": "custom augment",
                    },
                }
            )
        )

        # 読み込み
        config = Config.load_from_dir(config_dir)

        # 検証
        assert config.layouts.text_only.max_lines == 20
        assert config.layouts.text_only.prefer_assets == True
        assert config.layouts.two_column.left_max_lines == 15
        assert config.policy.density_range == (0.01, 0.02)
        assert config.policy.whitespace_range == (0.2, 0.5)
        assert config.policy.max_iterations == 5
        assert config.policy.commands.instruct_cmd == "custom instruct"

    def test_load_from_dir_without_files(self, temp_dir):
        """設定ファイルが存在しない場合はデフォルト設定を使用"""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        # 読み込み（ファイルなし）
        config = Config.load_from_dir(config_dir)

        # デフォルト設定が使われる
        assert config.layouts.text_only.max_lines == 18
        assert config.policy.density_range == (0.012, 0.018)
        assert config.policy.max_iterations == 3

    def test_load_invalid_yaml(self, temp_dir):
        """不正なYAMLはエラー"""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        # 不正なYAML
        layouts_yaml = config_dir / "layouts.yaml"
        layouts_yaml.write_text("invalid: yaml: content:")

        with pytest.raises(ValueError, match="Invalid YAML"):
            Config.load_from_dir(config_dir)

    def test_load_invalid_json(self, temp_dir):
        """不正なJSONはエラー"""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        # 不正なJSON
        policy_json = config_dir / "policy.json"
        policy_json.write_text("{invalid json}")

        with pytest.raises(ValueError, match="Invalid JSON"):
            Config.load_from_dir(config_dir)

    def test_get_default_layouts_yaml(self):
        """デフォルトのlayouts.yamlが取得できる"""
        yaml_content = Config.get_default_layouts_yaml()

        assert "text-only:" in yaml_content
        assert "max_lines: 18" in yaml_content
        assert "two-column:" in yaml_content

        # YAMLとしてパースできる
        data = yaml.safe_load(yaml_content)
        assert "layouts" in data

    def test_get_default_policy_json(self):
        """デフォルトのpolicy.jsonが取得できる"""
        json_content = Config.get_default_policy_json()

        # JSONとしてパースできる
        data = json.loads(json_content)
        assert "density_range" in data
        assert "whitespace_range" in data
        assert "max_iterations" in data
        assert "commands" in data

    def test_save_to_dir(self, temp_dir):
        """設定をディレクトリに保存できる"""
        config_dir = temp_dir / "config"
        config = Config(layouts=LayoutsConfig(), policy=PolicyConfig())

        config.save_to_dir(config_dir)

        # ファイルが作成されている
        assert (config_dir / "layouts.yaml").exists()
        assert (config_dir / "policy.json").exists()

        # 読み込める
        loaded_config = Config.load_from_dir(config_dir)
        assert loaded_config.layouts.text_only.max_lines == 18
        assert loaded_config.policy.max_iterations == 3
