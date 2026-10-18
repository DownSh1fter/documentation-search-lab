"""Download selected Python Tutorial pages and save sections as passages."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_VERSION = "3.15.0"
BASE_URL = f"https://docs.python.org/release/{DOCS_VERSION}/tutorial/"
LIBRARY_URL = f"https://docs.python.org/release/{DOCS_VERSION}/builtins/"
PAGES = {
    "introduction": "introduction.html",
    "controlflow": "controlflow.html",
    "datastructures": "datastructures.html",
    "modules": "modules.html",
    "inputoutput": "inputoutput.html",
    "errors": "errors.html",
    "classes": "classes.html",
}
MAX_WORDS = 220
OVERLAP_WORDS = 35


class _Section:
    def __init__(self, anchor: str) -> None:
        self.anchor = anchor
        self.title = ""
        self.text: list[str] = []


class _TutorialParser(HTMLParser):
    """Extract section text from Sphinx's article body, excluding nested sections."""

    _BLOCK_TAGS = {"p", "div", "pre", "li", "ul", "ol", "table", "tr", "br"}
    _HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_depth = 0
        self.section_stack: list[_Section] = []
        self.active_heading: str | None = None
        self.heading_text: list[str] = []
        self.skip_depth = 0
        self.sections: list[_Section] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "div":
            if self.body_depth:
                self.body_depth += 1
            elif "body" in (attributes.get("class") or "").split():
                self.body_depth = 1
        if not self.body_depth:
            return
        if tag in {"script", "style", "nav"}:
            self.skip_depth += 1
        if tag == "section":
            self.section_stack.append(_Section(attributes.get("id") or "section"))
        if tag in self._HEADING_TAGS:
            self.active_heading = tag
            self.heading_text = []
        if tag in self._BLOCK_TAGS and self.section_stack:
            self.section_stack[-1].text.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.body_depth:
            return
        if tag in {"script", "style", "nav"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == self.active_heading:
            if self.section_stack:
                self.section_stack[-1].title = " ".join("".join(self.heading_text).split())
            self.active_heading = None
        if tag in self._BLOCK_TAGS and self.section_stack:
            self.section_stack[-1].text.append(" ")
        if tag == "section" and self.section_stack:
            section = self.section_stack.pop()
            if section.title and " ".join("".join(section.text).split()):
                self.sections.append(section)
        if tag == "div":
            self.body_depth = max(0, self.body_depth - 1)

    def handle_data(self, data: str) -> None:
        if not self.body_depth or self.skip_depth:
            return
        if self.active_heading:
            self.heading_text.append(data)
        elif self.section_stack:
            self.section_stack[-1].text.append(data)


class _FunctionParser(HTMLParser):
    """Extract one documented Python built-in function from the built-ins reference."""

    _BLOCK_TAGS = {"p", "div", "pre", "li", "ul", "ol", "table", "tr", "br", "dt", "dd"}

    def __init__(self, function_id: str) -> None:
        super().__init__(convert_charrefs=True)
        self.function_id = function_id
        self.depth = 0
        self.found = False
        self.candidate_found = False
        self.candidate_text: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self.depth and tag == "dl" and "function" in (attributes.get("class") or "").split():
            self.depth = 1
            self.candidate_found = False
            self.candidate_text = []
        elif self.depth:
            self.depth += 1
        if self.depth and tag in self._BLOCK_TAGS:
            self.candidate_text.append(" ")
        if self.depth and attributes.get("id") == self.function_id:
            self.candidate_found = True

    def handle_endtag(self, tag: str) -> None:
        if self.depth:
            if tag in self._BLOCK_TAGS:
                self.candidate_text.append(" ")
            self.depth -= 1
            if not self.depth:
                if self.candidate_found:
                    self.text = self.candidate_text
                    self.found = True
                self.candidate_text = []

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.candidate_text.append(data)


def _download(url: str) -> str:
    request = Request(url, headers={"User-Agent": "doc-search-lab/0.1 learning project"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_passages() -> list[dict[str, str]]:
    passages: list[dict[str, str]] = []
    pages = [
        (page_id, BASE_URL + filename, None) for page_id, filename in PAGES.items()
    ]
    pages.append(("builtins", LIBRARY_URL + "functions.html", "open"))
    for page_id, page_url, only_anchor in pages:
        if only_anchor == "open":
            element_parser = _FunctionParser("open")
            element_parser.feed(_download(page_url))
            text = re.sub(r"\s+", " ", " ".join(element_parser.text)).strip()
            if not text:
                raise RuntimeError("Could not extract the built-in open() reference section")
            sections = [_Section("open")]
            sections[0].title = "open()"
            sections[0].text = [text]
        else:
            parser = _TutorialParser()
            parser.feed(_download(page_url))
            sections = parser.sections
        for section in sections:
            if only_anchor and section.anchor != only_anchor:
                continue
            text = re.sub(r"\s+", " ", " ".join(section.text)).strip()
            title = re.sub(r"[\s\u00b6]+$", "", section.title).strip()
            if len(text) < 80:
                continue
            words = text.split()
            chunks = _chunk_words(words)
            for part, chunk in enumerate(chunks, start=1):
                suffix = f"-part-{part:02d}" if len(chunks) > 1 else ""
                chunk_title = f"{title} (part {part})" if len(chunks) > 1 else title
                passages.append(
                    {
                        "id": f"{page_id}-{section.anchor}{suffix}",
                        "title": chunk_title,
                        "source_url": f"{page_url}#{section.anchor}",
                        "text": chunk,
                    }
                )
    return passages


def _chunk_words(words: list[str]) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + MAX_WORDS, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - OVERLAP_WORDS
    return chunks


def main() -> None:
    output_path = PROJECT_ROOT / "data" / "corpus.jsonl"
    passages = build_passages()
    if not passages:
        raise RuntimeError("No sections were extracted; check the documentation page structure")
    output_path.write_text(
        "".join(json.dumps(passage, ensure_ascii=False) + "\n" for passage in passages),
        encoding="utf-8",
    )
    print(f"Wrote {len(passages)} passages to {output_path}")
    for passage in passages[:10]:
        print(f"- {passage['id']}: {passage['title']}")


if __name__ == "__main__":
    main()
