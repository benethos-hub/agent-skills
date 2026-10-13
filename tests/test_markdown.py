"""Links, anchors, tables of contents and the text rules in every Markdown file.

External links are only fetched when LINKS_ONLINE=1 is set, because that
needs the network and the release links answer 404 before the first release.
"""

from __future__ import annotations

import os
import re
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from support import ROOT, headings, links, markdown_files, prose_lines, rel

EMOJI = re.compile("[\U0001f000-\U0001faff☀-➿⬀-⯿️]")
DASHES = re.compile("[–—]")


def anchors(path: Path) -> set[str]:
    return {h.anchor for h in headings(path.read_text(encoding="utf-8"))}


class LinkTest(unittest.TestCase):
    def test_relative_links_and_anchors(self):
        for path in markdown_files():
            for link in links(path.read_text(encoding="utf-8")):
                if re.match(r"^[a-z]+:", link.target):
                    continue
                where = f"{rel(path)}:{link.number}"
                target, _, fragment = link.target.partition("#")
                file = (path.parent / target).resolve() if target else path
                with self.subTest(link=f"{where} {link.target}"):
                    self.assertTrue(file.exists(), f"{where}: {target} does not exist")
                    self.assertTrue(file.is_relative_to(ROOT), f"{where}: {target} points outside the repository")
                    if fragment and file.suffix == ".md":
                        self.assertIn(fragment, anchors(file), f"{where}: no heading for #{fragment}")

    def test_links_to_this_repository_are_relative(self):
        # A link to a file of this repository on github.com shows main, not the
        # state the reader has in front of them. Release downloads are fine.
        own = re.compile(r"github\.com/benethos-hub/agent-skills/(blob|tree)/")
        for path in markdown_files():
            for link in links(path.read_text(encoding="utf-8")):
                with self.subTest(link=f"{rel(path)}:{link.number}"):
                    self.assertNotRegex(link.target, own, "use a relative link")

    @unittest.skipUnless(os.environ.get("LINKS_ONLINE") == "1", "set LINKS_ONLINE=1 to fetch external links")
    def test_external_links_answer(self):
        seen: dict[str, str] = {}
        for path in markdown_files():
            for link in links(path.read_text(encoding="utf-8")):
                if link.target.startswith(("http://", "https://")):
                    seen.setdefault(link.target.split("#")[0], f"{rel(path)}:{link.number}")
        for url, where in sorted(seen.items()):
            with self.subTest(url=url):
                self.assertIsNone(fetch_error(url), f"{where}: {url}")


def fetch_error(url: str) -> str | None:
    headers = {"User-Agent": "agent-skills link check"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=20):
                return None
        except urllib.error.HTTPError as error:
            error.close()
            # Some servers refuse HEAD but answer GET.
            if method == "HEAD" and error.code in (403, 405):
                continue
            return f"HTTP {error.code}"
        except (urllib.error.URLError, TimeoutError) as error:
            return str(error)
    return "no answer"


class ContentsTest(unittest.TestCase):
    """A **Contents** list names every ## and ### heading, in order."""

    def test_contents_match_headings(self):
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            listed = contents(text)
            if listed is None:
                continue
            expected = [(h.level - 2, h.anchor) for h in headings(text) if h.level in (2, 3)]
            with self.subTest(file=rel(path)):
                self.assertEqual(listed, expected)


def contents(text: str) -> list[tuple[int, str]] | None:
    lines = text.splitlines()
    if "**Contents**" not in lines:
        return None
    entries: list[tuple[int, str]] = []
    for line in lines[lines.index("**Contents**") + 1 :]:
        if not line.strip():
            if entries:
                break
            continue
        match = re.match(r"^( *)- \[[^\]]*\]\(#([^)]+)\)$", line)
        if not match:
            break
        entries.append((len(match.group(1)) // 2, match.group(2)))
    return entries


class TextRulesTest(unittest.TestCase):
    """The writing rules of this repository, for the text a reader sees."""

    def check(self, pattern: re.Pattern, what: str):
        for path in markdown_files():
            for line in prose_lines(path.read_text(encoding="utf-8")):
                with self.subTest(line=f"{rel(path)}:{line.number}"):
                    self.assertIsNone(pattern.search(line.text), f"{what}: {line.text.strip()}")

    def test_no_semicolons(self):
        self.check(re.compile(";"), "semicolon")

    def test_no_em_or_en_dashes(self):
        self.check(DASHES, "em or en dash")

    def test_no_emojis(self):
        self.check(EMOJI, "emoji")


if __name__ == "__main__":
    unittest.main()
