"""
設定ファイル管理モジュール

layouts.yaml と policy.json の読み込み・検証・管理機能を提供します。
"""

import json
import yaml
from pathlib import Path
from typing import Tuple
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ===============================
# Layouts スキーマ
# ===============================


class TextOnlyLayout(BaseModel):
    """テキストのみのレイアウト"""

    max_lines: int = Field(default=18, description="最大行数")
    prefer_assets: bool = Field(default=False, description="資材を優先するか")


class TwoColumnLayout(BaseModel):
    """2カラムレイアウト"""

    left_max_lines: int = Field(default=10, description="左カラムの最大行数")
    right_max_lines: int = Field(default=10, description="右カラムの最大行数")


class ImageRightLayout(BaseModel):
    """右側に画像を配置するレイアウト"""

    text_max_lines: int = Field(default=12, description="テキスト部分の最大行数")
    image_width_pct: int = Field(default=40, description="画像の幅（%）")


class QuoteSlideLayout(BaseModel):
    """引用スライドのレイアウト"""

    max_lines: int = Field(default=6, description="最大行数")


class LayoutsConfig(BaseModel):
    """レイアウト設定全体"""

    model_config = ConfigDict(extra="allow")  # 追加のレイアウト定義を許可

    text_only: TextOnlyLayout = Field(default_factory=TextOnlyLayout)
    two_column: TwoColumnLayout = Field(default_factory=TwoColumnLayout)
    image_right: ImageRightLayout = Field(default_factory=ImageRightLayout)
    quote_slide: QuoteSlideLayout = Field(default_factory=QuoteSlideLayout)


# ===============================
# Policy スキーマ
# ===============================


class CommandsConfig(BaseModel):
    """外部コマンド設定"""

    instruct_cmd: str = Field(
        default="echo 'LLM CLI not configured'", description="instruct コマンド"
    )
    build_cmd: str = Field(default="echo 'LLM CLI not configured'", description="build コマンド")
    augment_cmd: str = Field(
        default="echo 'LLM CLI not configured'", description="augment コマンド"
    )


class PolicyConfig(BaseModel):
    """ポリシー設定"""

    density_range: Tuple[float, float] = Field(
        default=(0.012, 0.018), description="文字密度の許容範囲"
    )
    whitespace_range: Tuple[float, float] = Field(
        default=(0.15, 0.40), description="余白率の許容範囲"
    )
    max_iterations: int = Field(default=3, description="最大反復回数")
    commands: CommandsConfig = Field(default_factory=CommandsConfig, description="外部コマンド設定")

    @field_validator("density_range")
    @classmethod
    def validate_density_range(cls, v):
        if v[0] >= v[1]:
            raise ValueError("density_range: min must be less than max")
        if v[0] < 0 or v[1] > 1:
            raise ValueError("density_range: values must be between 0 and 1")
        return v

    @field_validator("whitespace_range")
    @classmethod
    def validate_whitespace_range(cls, v):
        if v[0] >= v[1]:
            raise ValueError("whitespace_range: min must be less than max")
        if v[0] < 0 or v[1] > 1:
            raise ValueError("whitespace_range: values must be between 0 and 1")
        return v

    @field_validator("max_iterations")
    @classmethod
    def validate_max_iterations(cls, v):
        if v < 1:
            raise ValueError("max_iterations must be at least 1")
        return v


# ===============================
# 設定管理クラス
# ===============================


class Config:
    """設定ファイル管理クラス

    layouts.yaml と policy.json の読み込み・検証機能を提供します。

    Attributes:
        layouts: レイアウト設定
        policy: ポリシー設定

    Examples:
        >>> config = Config.load_from_dir(Path("config"))
        >>> config.layouts.text_only.max_lines
        18
    """

    def __init__(self, layouts: LayoutsConfig, policy: PolicyConfig):
        """設定を初期化

        Args:
            layouts: レイアウト設定
            policy: ポリシー設定
        """
        self.layouts = layouts
        self.policy = policy

    @classmethod
    def load_from_dir(cls, config_dir: Path) -> "Config":
        """設定ディレクトリから設定を読み込む

        Args:
            config_dir: 設定ディレクトリのパス

        Returns:
            設定オブジェクト

        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合
            ValueError: 設定ファイルの形式が不正な場合
        """
        layouts_path = config_dir / "layouts.yaml"
        policy_path = config_dir / "policy.json"

        # layouts.yaml の読み込み
        if layouts_path.exists():
            layouts = cls._load_layouts(layouts_path)
        else:
            layouts = LayoutsConfig()  # デフォルト設定を使用

        # policy.json の読み込み
        if policy_path.exists():
            policy = cls._load_policy(policy_path)
        else:
            policy = PolicyConfig()  # デフォルト設定を使用

        return cls(layouts=layouts, policy=policy)

    @classmethod
    def _load_layouts(cls, path: Path) -> LayoutsConfig:
        """layouts.yaml を読み込む

        Args:
            path: layouts.yaml のパス

        Returns:
            レイアウト設定

        Raises:
            ValueError: YAML形式が不正な場合
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # YAML の layouts キーを取得
            layouts_data = data.get("layouts", {})

            # Pydantic モデルに変換
            return LayoutsConfig(
                text_only=layouts_data.get("text-only", {}),
                two_column=layouts_data.get("two-column", {}),
                image_right=layouts_data.get("image-right", {}),
                quote_slide=layouts_data.get("quote-slide", {}),
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading layouts from {path}: {e}")

    @classmethod
    def _load_policy(cls, path: Path) -> PolicyConfig:
        """policy.json を読み込む

        Args:
            path: policy.json のパス

        Returns:
            ポリシー設定

        Raises:
            ValueError: JSON形式が不正な場合
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return PolicyConfig(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading policy from {path}: {e}")

    @classmethod
    def get_default_layouts_yaml(cls) -> str:
        """デフォルトの layouts.yaml を取得

        Returns:
            デフォルトの layouts.yaml の内容
        """
        return """layouts:
  text-only:
    max_lines: 18
    prefer_assets: false

  two-column:
    left_max_lines: 10
    right_max_lines: 10

  image-right:
    text_max_lines: 12
    image_width_pct: 40

  quote-slide:
    max_lines: 6
"""

    @classmethod
    def get_default_policy_json(cls) -> str:
        """デフォルトの policy.json を取得

        Returns:
            デフォルトの policy.json の内容
        """
        default_policy = PolicyConfig()
        return json.dumps(
            {
                "density_range": list(default_policy.density_range),
                "whitespace_range": list(default_policy.whitespace_range),
                "max_iterations": default_policy.max_iterations,
                "commands": {
                    "instruct_cmd": default_policy.commands.instruct_cmd,
                    "build_cmd": default_policy.commands.build_cmd,
                    "augment_cmd": default_policy.commands.augment_cmd,
                },
            },
            indent=2,
        )

    def save_to_dir(self, config_dir: Path) -> None:
        """設定をディレクトリに保存

        Args:
            config_dir: 設定ディレクトリのパス
        """
        config_dir.mkdir(parents=True, exist_ok=True)

        # layouts.yaml を保存
        layouts_path = config_dir / "layouts.yaml"
        with open(layouts_path, "w", encoding="utf-8") as f:
            f.write(self.get_default_layouts_yaml())

        # policy.json を保存
        policy_path = config_dir / "policy.json"
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(self.get_default_policy_json())
