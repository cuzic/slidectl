"""
Markdown正規化・構造解析モジュール

入力Markdownファイルを正規化し、章/スライド候補を抽出します。
"""

import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class SlideHint(BaseModel):
    """スライドヒント"""

    hint_id: str = Field(description="ヒントID")
    title: str = Field(description="タイトル")
    bullets: List[str] = Field(default_factory=list, description="箇条書きリスト")
    raw_text: str = Field(description="生テキスト")


class Section(BaseModel):
    """セクション"""

    section_id: str = Field(description="セクションID")
    heading: str = Field(description="見出し")
    slides_hint: List[SlideHint] = Field(default_factory=list, description="スライドヒントリスト")


class DocumentStructure(BaseModel):
    """ドキュメント構造"""

    version: str = Field(default="1.0", description="バージョン")
    doc_title: str = Field(description="ドキュメントタイトル")
    sections: List[Section] = Field(default_factory=list, description="セクションリスト")


class MarkdownIngestor:
    """Markdown構造解析クラス

    Markdownファイルを読み込み、正規化と構造抽出を行います。

    Examples:
        >>> ingestor = MarkdownIngestor()
        >>> structure = ingestor.process(Path("input.md"))
        >>> ingestor.save_outputs(Path("workspace/ingest"), structure)
    """

    def __init__(self):
        """構造解析器を初期化"""
        pass

    def process(self, input_file: Path) -> tuple[str, DocumentStructure]:
        """Markdownファイルを処理

        Args:
            input_file: 入力Markdownファイルのパス

        Returns:
            (normalized_content, structure) のタプル

        Raises:
            FileNotFoundError: 入力ファイルが存在しない場合
            ValueError: Markdown形式が不正な場合
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # ファイルを読み込む
        content = input_file.read_text(encoding="utf-8")

        # 正規化
        normalized = self._normalize_markdown(content)

        # 構造抽出
        structure = self._extract_structure(normalized)

        return normalized, structure

    def _normalize_markdown(self, content: str) -> str:
        """Markdownを正規化

        Args:
            content: Markdown文字列

        Returns:
            正規化されたMarkdown文字列
        """
        # 改行コードを統一
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")

        # 複数の空行を2行に統一
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)

        # 行末の空白を削除
        lines = [line.rstrip() for line in normalized.split("\n")]
        normalized = "\n".join(lines)

        # 末尾に改行を追加
        if not normalized.endswith("\n"):
            normalized += "\n"

        return normalized

    def _extract_structure(self, content: str) -> DocumentStructure:
        """Markdown構造を抽出

        Args:
            content: 正規化されたMarkdown文字列

        Returns:
            ドキュメント構造
        """
        lines = content.split("\n")

        # タイトルを抽出（最初のH1見出し）
        doc_title = "Untitled Document"
        for line in lines:
            if line.startswith("# "):
                doc_title = line[2:].strip()
                break

        # セクション構造を抽出
        sections = self._extract_sections(lines)

        return DocumentStructure(
            version="1.0",
            doc_title=doc_title,
            sections=sections,
        )

    def _extract_sections(self, lines: List[str]) -> List[Section]:
        """セクション構造を抽出

        Args:
            lines: Markdown行のリスト

        Returns:
            セクションリスト
        """
        sections: List[Section] = []
        current_section: Optional[Section] = None
        current_subsection_lines: List[str] = []
        section_counter = 0
        hint_counter = 0

        for i, line in enumerate(lines):
            # H2見出し（セクション開始）
            if line.startswith("## "):
                # 前のサブセクションを処理
                if current_section and current_subsection_lines:
                    hint = self._create_slide_hint(current_subsection_lines, hint_counter)
                    if hint:
                        current_section.slides_hint.append(hint)
                        hint_counter += 1
                    current_subsection_lines = []

                # 前のセクションを保存
                if current_section:
                    sections.append(current_section)

                # 新しいセクション開始
                section_counter += 1
                current_section = Section(
                    section_id=f"sec-{section_counter:03d}",
                    heading=line[3:].strip(),
                    slides_hint=[],
                )

            # H3見出し（サブセクション/スライドヒント）
            elif line.startswith("### "):
                # 前のサブセクションを処理
                if current_section and current_subsection_lines:
                    hint = self._create_slide_hint(current_subsection_lines, hint_counter)
                    if hint:
                        current_section.slides_hint.append(hint)
                        hint_counter += 1

                # 新しいサブセクション開始
                current_subsection_lines = [line]

            # 通常の行
            else:
                if current_section:
                    current_subsection_lines.append(line)

        # 最後のサブセクションを処理
        if current_section and current_subsection_lines:
            hint = self._create_slide_hint(current_subsection_lines, hint_counter)
            if hint:
                current_section.slides_hint.append(hint)

        # 最後のセクションを保存
        if current_section:
            sections.append(current_section)

        return sections

    def _create_slide_hint(self, lines: List[str], counter: int) -> Optional[SlideHint]:
        """スライドヒントを作成

        Args:
            lines: サブセクションの行リスト
            counter: ヒントカウンター

        Returns:
            スライドヒント（内容がない場合はNone）
        """
        if not lines:
            return None

        # タイトルを抽出（H3見出し）
        title = "Untitled"
        content_lines = []

        for line in lines:
            if line.startswith("### "):
                title = line[4:].strip()
            elif line.strip():  # 空行でない
                content_lines.append(line)

        # 箇条書きを抽出
        bullets = []
        raw_text_lines = []

        for line in content_lines:
            stripped = line.strip()
            # 箇条書き（-, *, +）
            if re.match(r"^[-*+]\s+", stripped):
                bullet_text = re.sub(r"^[-*+]\s+", "", stripped)
                bullets.append(bullet_text)
                raw_text_lines.append(line)
            # 番号付き箇条書き
            elif re.match(r"^\d+\.\s+", stripped):
                bullet_text = re.sub(r"^\d+\.\s+", "", stripped)
                bullets.append(bullet_text)
                raw_text_lines.append(line)
            else:
                raw_text_lines.append(line)

        raw_text = "\n".join(raw_text_lines).strip()

        # 内容がなければNone
        if not raw_text and not bullets:
            return None

        return SlideHint(
            hint_id=f"h-{counter+1:03d}",
            title=title,
            bullets=bullets,
            raw_text=raw_text,
        )

    def save_outputs(
        self, output_dir: Path, normalized_content: str, structure: DocumentStructure
    ) -> tuple[Path, Path]:
        """出力ファイルを保存

        Args:
            output_dir: 出力ディレクトリ
            normalized_content: 正規化されたMarkdown
            structure: ドキュメント構造

        Returns:
            (normalized.md のパス, structure.json のパス) のタプル
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # normalized.md を保存
        normalized_path = output_dir / "normalized.md"
        normalized_path.write_text(normalized_content, encoding="utf-8")

        # structure.json を保存
        structure_path = output_dir / "structure.json"
        structure_path.write_text(
            structure.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8"
        )

        return normalized_path, structure_path
