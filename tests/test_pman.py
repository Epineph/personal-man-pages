"""Behavior checks for the starter's links, views, adapters and exports."""

from pathlib import Path
from unittest.mock import patch
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from pmanlib.catalog import Catalog
from pmanlib.document import HelpError, parse_document, read_document
from pmanlib.export import save_document


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations"))
from pman_help import show_requested_help


def invoke(*arguments: str, environment: dict | None = None):
  return subprocess.run(
    [sys.executable, str(ROOT / "bin" / "pman"), *arguments],
    text=True, encoding="utf-8", capture_output=True, check=False,
    env=environment, cwd=ROOT,
  )


class PageTests(unittest.TestCase):
  def test_example_view_does_not_include_theory(self):
    text = read_document(ROOT / "pages" / "zscore.md").select("examples")
    self.assertIn("## Examples", text)
    self.assertNotIn("## Definition and denominator", text)
    self.assertNotIn("pman:section", text)

  def test_technical_view_and_section_order(self):
    document = read_document(ROOT / "pages" / "zscore.md")
    text = document.select("technical")
    self.assertIn("## Worked example", text)
    self.assertNotIn("## Practical use", text)
    text = document.select(identifiers=["worked-example", "theory"])
    self.assertLess(text.index("## Definition"), text.index("## Worked"))

  def test_fenced_marker_is_literal(self):
    text = (
      "# Demo\n<!-- pman:section examples views=examples -->\n"
      "## Examples\n````markdown\n"
      "<!-- pman:section fake views=technical -->\n```\n````\n"
    )
    document = parse_document(text)
    self.assertEqual(len(document.sections), 1)
    self.assertIn("pman:section fake", document.select("examples"))

  def test_bad_markers_and_duplicate_sections_fail(self):
    for text in (
      "# D\n<!-- pman:section x views=unknown -->\n## X\n",
      "# D\n<!-- pman:secton x views=long -->\n## X\n",
      "# D\n<!-- pman:section x views=long -->\n## X\n"
      "<!-- pman:section x views=brief -->\n## Again\n",
    ):
      with self.subTest(text=text), self.assertRaises(HelpError):
        parse_document(text)

  def test_missing_optional_view_is_an_error(self):
    document = read_document(ROOT / "pages" / "croot.md")
    with self.assertRaises(HelpError):
      document.select("technical")

  def test_aliases_and_unknown_names(self):
    catalog = Catalog(ROOT)
    self.assertEqual(catalog.resolve("zscore").identifier, "demo.zscore")
    with self.assertRaises(HelpError):
      catalog.resolve("not-registered")

  def test_catalog_rejects_collisions_and_path_escape(self):
    catalog = Catalog(ROOT)
    for field, value in (("aliases", ["pman"]), ("file", "../outside.md")):
      data = json.loads(json.dumps(catalog.data))
      data["pages"][1][field] = value
      with self.subTest(field=field), self.assertRaises(HelpError):
        catalog.validate(data)

  def test_new_page_and_alias_are_registered(self):
    with tempfile.TemporaryDirectory() as d:
      root = Path(d)
      (root / "registry.json").write_text('{"schema":1,"pages":[]}')
      shutil.copytree(ROOT / "templates", root / "templates")
      catalog = Catalog(root)
      path = catalog.create("tools.example", "Example", ["example"])
      self.assertTrue(path.is_file())
      self.assertEqual(Catalog(root).resolve("example").path, path)


class IntegrationTests(unittest.TestCase):
  def test_check_and_equals_paging_syntax(self):
    result = invoke("--check")
    self.assertEqual(result.returncode, 0, result.stderr)
    result = invoke("zscore", "--technical-help", "--paging=never")
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("## Worked example", result.stdout)

  def test_adapter_does_not_intercept_operands_or_all_by_default(self):
    self.assertIsNone(show_requested_help("x", ["--", "--long-help"]))
    self.assertIsNone(show_requested_help("x", ["--all"]))
    with patch("pman_help.call_pman", return_value=2) as call:
      self.assertEqual(show_requested_help("x", ["--long-help"]), 2)
      call.assert_called_once()

  def test_bash_help_and_work(self):
    for args, expected in (
      (["Heini"], "Hello, Heini."),
      (["--long-help", "--paging", "never"], "## Examples"),
      (["--", "--long-help"], "Hello, --long-help."),
    ):
      result = subprocess.run(
        ["bash", str(ROOT / "examples" / "greet.sh"), *args],
        text=True, capture_output=True, cwd=ROOT,
      )
      self.assertEqual(result.returncode, 0, result.stderr)
      self.assertIn(expected, result.stdout)

  def test_numerical_example(self):
    result = subprocess.run(
      [sys.executable, str(ROOT / "examples" / "zscore.py"), "2", "4", "6"],
      text=True, capture_output=True,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(
      result.stdout.splitlines(), ["-1.000000", "0.000000", "1.000000"]
    )

  def test_function_help_does_not_change_directory(self):
    script = (
      'source "$PMAN_HOME/integrations/pman.sh"\n'
      'source "$PMAN_HOME/examples/croot.sh"\n'
      'before="$PWD"\n'
      'croot --long-help --paging never >/dev/null || exit $?\n'
      '[[ "$PWD" == "$before" ]]\n'
    )
    environment = dict(
      os.environ, PMAN_HOME=str(ROOT), PMAN_BIN=str(ROOT / "bin/pman")
    )
    for shell in ("bash", "zsh"):
      if shutil.which(shell):
        result = subprocess.run([shell, "-c", script], env=environment)
        self.assertEqual(result.returncode, 0)


class ExportTests(unittest.TestCase):
  def test_quiet_markdown_export_and_log(self):
    with tempfile.TemporaryDirectory() as d:
      output, log = Path(d) / "help.md", Path(d) / "help.log"
      result = invoke(
        "zscore", "--technical-help", "--save-only", str(output),
        "--save-log", str(log),
      )
      self.assertEqual(result.returncode, 0, result.stderr)
      self.assertEqual(result.stdout, "")
      self.assertIn("## Worked example", output.read_text())
      self.assertIn("Saved", log.read_text())
      again = invoke("zscore", "--save-only", str(output))
      self.assertEqual(again.returncode, 2)
      self.assertIn("## Worked example", output.read_text())

  def test_missing_pandoc_leaves_output_absent(self):
    with tempfile.TemporaryDirectory() as d:
      output = Path(d) / "help.html"
      with patch("pmanlib.export.shutil.which", return_value=None):
        with self.assertRaisesRegex(HelpError, "Pandoc is not on PATH"):
          save_document("# Test\n\n## Example\n", "Test", output, ROOT, ROOT)
      self.assertFalse(output.exists())

  def test_converter_failure_preserves_existing_export(self):
    with tempfile.TemporaryDirectory() as d:
      output = Path(d) / "help.html"
      output.write_text("previous export")
      completed = subprocess.CompletedProcess([], 2, "", "conversion failed")
      with patch("pmanlib.export.shutil.which", return_value="pandoc"):
        with patch("pmanlib.export.subprocess.run", return_value=completed):
          with self.assertRaisesRegex(HelpError, "conversion failed"):
            save_document("# T\n\n## E\n", "T", output, ROOT, ROOT, force=True)
      self.assertEqual(output.read_text(), "previous export")

  def test_save_only_with_separate_save_flag(self):
    with tempfile.TemporaryDirectory() as d:
      result = invoke(
        "greet", "--all", "--save", str(Path(d)/"greet.md"), "--save-only"
      )
      self.assertEqual(result.returncode, 0, result.stderr)
      self.assertEqual(result.stdout, "")


if __name__ == "__main__":
  unittest.main()
