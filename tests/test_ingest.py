"""
Markdown構造解析のテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json

from slidectl.ingest import (
    MarkdownIngestor,
    DocumentStructure,
    Section,
    SlideHint,
)


class TestMarkdownIngestor:
    """MarkdownIngestorクラスのテスト"""

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def ingestor(self):
        """MarkdownIngestorインスタンスを作成"""
        return MarkdownIngestor()

    @pytest.fixture
    def sample_markdown(self, temp_dir):
        """サンプルMarkdownファイルを作成"""
        content = """# プレゼンテーションタイトル

## 序章

### 課題意識

- 背景
- 現状
- 課題

### 解決アプローチ

1. 方針A
2. 方針B

## 本論

### 提案手法

本文テキストがここに入ります。

- ポイント1
- ポイント2

### 実験結果

実験結果の説明文です。

## まとめ

### 結論

- 結論1
- 結論2
"""
        md_file = temp_dir / "test.md"
        md_file.write_text(content, encoding="utf-8")
        return md_file

    def test_normalize_markdown(self, ingestor):
        """Markdown正規化が正しく動作する"""
        content = "# Title\r\n\r\n\r\n\r\nText   \r\n\r\n"

        normalized = ingestor._normalize_markdown(content)

        # 改行コード統一
        assert "\r" not in normalized
        # 複数の空行を2行に統一
        assert "\n\n\n" not in normalized
        # 行末の空白削除
        assert "Text   \n" not in normalized
        assert "Text\n" in normalized
        # 末尾に改行
        assert normalized.endswith("\n")

    def test_extract_structure_basic(self, ingestor, sample_markdown):
        """基本的な構造抽出が正しく動作する"""
        content = sample_markdown.read_text(encoding="utf-8")
        normalized = ingestor._normalize_markdown(content)

        structure = ingestor._extract_structure(normalized)

        assert structure.version == "1.0"
        assert structure.doc_title == "プレゼンテーションタイトル"
        assert len(structure.sections) == 3
        assert structure.sections[0].heading == "序章"
        assert structure.sections[1].heading == "本論"
        assert structure.sections[2].heading == "まとめ"

    def test_extract_slide_hints(self, ingestor, sample_markdown):
        """スライドヒントの抽出が正しく動作する"""
        content = sample_markdown.read_text(encoding="utf-8")
        normalized = ingestor._normalize_markdown(content)
        structure = ingestor._extract_structure(normalized)

        # 序章のスライドヒント
        assert len(structure.sections[0].slides_hint) == 2
        hint1 = structure.sections[0].slides_hint[0]
        assert hint1.title == "課題意識"
        assert len(hint1.bullets) == 3
        assert "背景" in hint1.bullets
        assert "現状" in hint1.bullets
        assert "課題" in hint1.bullets

        hint2 = structure.sections[0].slides_hint[1]
        assert hint2.title == "解決アプローチ"
        assert len(hint2.bullets) == 2
        assert "方針A" in hint2.bullets
        assert "方針B" in hint2.bullets

    def test_process_file(self, ingestor, sample_markdown):
        """ファイル処理が正しく動作する"""
        normalized, structure = ingestor.process(sample_markdown)

        assert isinstance(normalized, str)
        assert isinstance(structure, DocumentStructure)
        assert structure.doc_title == "プレゼンテーションタイトル"
        assert len(structure.sections) > 0

    def test_process_nonexistent_file(self, ingestor, temp_dir):
        """存在しないファイルの処理はエラー"""
        nonexistent = temp_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            ingestor.process(nonexistent)

    def test_save_outputs(self, ingestor, temp_dir):
        """出力ファイルの保存が正しく動作する"""
        normalized_content = "# Test\n\nContent\n"
        structure = DocumentStructure(
            version="1.0",
            doc_title="Test Doc",
            sections=[
                Section(
                    section_id="sec-001",
                    heading="Section 1",
                    slides_hint=[
                        SlideHint(
                            hint_id="h-001",
                            title="Hint 1",
                            bullets=["a", "b"],
                            raw_text="test",
                        )
                    ],
                )
            ],
        )

        output_dir = temp_dir / "output"
        normalized_path, structure_path = ingestor.save_outputs(
            output_dir, normalized_content, structure
        )

        # ファイルが作成される
        assert normalized_path.exists()
        assert structure_path.exists()
        assert normalized_path.name == "normalized.md"
        assert structure_path.name == "structure.json"

        # 内容を確認
        assert normalized_path.read_text(encoding="utf-8") == normalized_content

        structure_data = json.loads(structure_path.read_text(encoding="utf-8"))
        assert structure_data["doc_title"] == "Test Doc"
        assert len(structure_data["sections"]) == 1

    def test_extract_sections_with_no_subsections(self, ingestor):
        """サブセクションのないセクションを処理できる"""
        content = """# Title

## Section 1

Some content without subsections.

## Section 2

More content.
"""
        normalized = ingestor._normalize_markdown(content)
        structure = ingestor._extract_structure(normalized)

        assert len(structure.sections) == 2
        assert structure.sections[0].heading == "Section 1"
        assert structure.sections[1].heading == "Section 2"

    def test_empty_document(self, ingestor):
        """空のドキュメントを処理できる"""
        content = ""
        normalized = ingestor._normalize_markdown(content)
        structure = ingestor._extract_structure(normalized)

        assert structure.doc_title == "Untitled Document"
        assert len(structure.sections) == 0

    def test_unicode_content(self, ingestor, temp_dir):
        """Unicode文字を含むMarkdownを処理できる"""
        content = """# 日本語タイトル

## セクション🎉

### サブセクション

- 項目１
- 項目２
"""
        md_file = temp_dir / "unicode.md"
        md_file.write_text(content, encoding="utf-8")

        normalized, structure = ingestor.process(md_file)

        assert structure.doc_title == "日本語タイトル"
        assert structure.sections[0].heading == "セクション🎉"
        assert structure.sections[0].slides_hint[0].title == "サブセクション"

    def test_section_ids_are_unique(self, ingestor, sample_markdown):
        """セクションIDがユニークである"""
        content = sample_markdown.read_text(encoding="utf-8")
        normalized = ingestor._normalize_markdown(content)
        structure = ingestor._extract_structure(normalized)

        section_ids = [s.section_id for s in structure.sections]
        assert len(section_ids) == len(set(section_ids))  # 重複なし

    def test_hint_ids_are_unique(self, ingestor, sample_markdown):
        """ヒントIDがユニークである"""
        content = sample_markdown.read_text(encoding="utf-8")
        normalized = ingestor._normalize_markdown(content)
        structure = ingestor._extract_structure(normalized)

        all_hint_ids = []
        for section in structure.sections:
            for hint in section.slides_hint:
                all_hint_ids.append(hint.hint_id)

        assert len(all_hint_ids) == len(set(all_hint_ids))  # 重複なし
