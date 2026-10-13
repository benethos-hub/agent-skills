"""The layout of the repository and the header of every skill."""

from __future__ import annotations

import re
import unittest

from support import ROOT, categories, rel, skill_folders, skills

# Fields the Agent Skills specification defines for the header.
HEADER_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
COMPATIBILITY_MAX = 500

# What a skill folder may hold. evals/ stays out of the ZIPs.
SKILL_ENTRIES = {"SKILL.md", "references", "scripts", "assets", "evals", "LICENSE.txt"}

# The specification recommends keeping SKILL.md below this and moving
# longer material into references/.
SKILL_MD_MAX_LINES = 500


class RootTest(unittest.TestCase):
    def test_root_files(self):
        for name in ("README.md", "LICENSE"):
            self.assertTrue((ROOT / name).is_file(), f"{name} is missing")

    def test_license_is_mit(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License"), "LICENSE does not start with 'MIT License'")
        self.assertRegex(text, r"Copyright \(c\) \d{4} \S")

    def test_there_is_a_category(self):
        self.assertTrue(categories(), "no category folder found")


class CategoryTest(unittest.TestCase):
    def test_category_names(self):
        for category in categories():
            with self.subTest(category=category.name):
                self.assertRegex(category.name, skills.NAME_PATTERN, "category names are lower case")

    def test_category_has_readme(self):
        for category in categories():
            with self.subTest(category=category.name):
                self.assertTrue((category / "README.md").is_file(), f"{category.name}/README.md is missing")

    def test_category_holds_only_skills(self):
        for category in categories():
            folders = skill_folders(category)
            with self.subTest(category=category.name):
                self.assertTrue(folders, f"{category.name} holds no skill")
            for folder in folders:
                with self.subTest(folder=rel(folder)):
                    self.assertTrue((folder / "SKILL.md").is_file(), f"{rel(folder)} has no SKILL.md")
            loose = sorted(p.name for p in category.iterdir() if p.is_file() and p.name != "README.md")
            with self.subTest(category=category.name):
                self.assertEqual(loose, [], f"files in {category.name} besides README.md")


class SkillTest(unittest.TestCase):
    def setUp(self):
        self.folders = [f for c in categories() for f in skill_folders(c)]

    def test_skills_pass_the_packaging_check(self):
        # The same check the release runs. It exits with a list of problems.
        try:
            loaded = skills.load_skills()
        except SystemExit as error:
            self.fail(f"skills.py rejects the skills: {error}")
        self.assertEqual(sorted(s.folder for s in loaded), sorted(self.folders))

    def test_header_fields(self):
        for folder in self.folders:
            header = skills.read_header(folder / "SKILL.md")
            with self.subTest(skill=rel(folder)):
                unknown = sorted(set(header) - HEADER_FIELDS)
                self.assertEqual(unknown, [], "fields outside the Agent Skills specification")
                self.assertLessEqual(len(header.get("compatibility", "")), COMPATIBILITY_MAX)

    def test_license_is_named(self):
        for folder in self.folders:
            header = skills.read_header(folder / "SKILL.md")
            with self.subTest(skill=rel(folder)):
                self.assertEqual(header.get("license"), "MIT")

    def test_skill_folder_entries(self):
        for folder in self.folders:
            with self.subTest(skill=rel(folder)):
                extra = sorted(p.name for p in folder.iterdir() if p.name not in SKILL_ENTRIES)
                self.assertEqual(extra, [], f"allowed are {', '.join(sorted(SKILL_ENTRIES))}")

    def test_skill_md_length(self):
        for folder in self.folders:
            lines = (folder / "SKILL.md").read_text(encoding="utf-8").count("\n")
            with self.subTest(skill=rel(folder)):
                self.assertLess(lines, SKILL_MD_MAX_LINES, "move longer material into references/")

    def test_body_has_a_title(self):
        for folder in self.folders:
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            body = text.split("\n---", 1)[1] if text.startswith("---") else text
            with self.subTest(skill=rel(folder)):
                self.assertRegex(body, re.compile(r"^# \S", re.MULTILINE), "no # title below the header")


if __name__ == "__main__":
    unittest.main()
