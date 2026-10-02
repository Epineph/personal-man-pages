"""Verify help routing and delegation without contacting package services."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "wrappers" / "search-python-packages"


class SearchHelpLinkTests(unittest.TestCase):
  def test_help_works_without_the_original_command(self):
    environment = dict(
      os.environ, SEARCH_PYTHON_PACKAGES_ORIGINAL="/missing/original-command"
    )
    result = subprocess.run(
      ["bash", str(WRAPPER), "--long-help", "--paging", "never"],
      env=environment, text=True, capture_output=True,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("## Search workflow", result.stdout)

  def test_normal_arguments_and_status_are_preserved(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      original = root / "original"
      capture = root / "arguments.json"
      original.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import json, os, sys\n"
        "Path(os.environ['CAPTURE']).write_text(json.dumps(sys.argv[1:]))\n"
        "raise SystemExit(29)\n"
      )
      original.chmod(0o755)
      environment = dict(
        os.environ, SEARCH_PYTHON_PACKAGES_ORIGINAL=str(original),
        CAPTURE=str(capture),
      )
      arguments = ["two words", "--csv", "a file.csv", "--all"]
      result = subprocess.run(
        ["bash", str(WRAPPER), *arguments], env=environment,
        text=True, capture_output=True,
      )
      self.assertEqual(result.returncode, 29, result.stderr)
      self.assertEqual(json.loads(capture.read_text()), arguments)

  def test_missing_original_is_reported_for_a_search(self):
    environment = dict(
      os.environ, SEARCH_PYTHON_PACKAGES_ORIGINAL="/missing/original-command"
    )
    result = subprocess.run(
      ["bash", str(WRAPPER), "markdown"], env=environment,
      text=True, capture_output=True,
    )
    self.assertEqual(result.returncode, 127)
    self.assertIn("Original command is missing", result.stderr)


if __name__ == "__main__":
  unittest.main()
