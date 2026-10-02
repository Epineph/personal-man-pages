"""Copy beside a Python script, or add this directory to its import path."""

from collections.abc import Sequence
from pathlib import Path
import os
import subprocess
import sys


EXTENDED_FLAGS = frozenset({
  "--long-help", "--detailed", "--detailed-help", "--technical-help",
  "--all-help", "--list-examples",
})


def call_pman(
  page: str, arguments: Sequence[str], viewer: str | Path | None = None
) -> int:
  executable = str(viewer or os.environ.get("PMAN_BIN", "pman"))
  try:
    return subprocess.run(
      [executable, page, *arguments], check=False
    ).returncode
  except OSError as exc:
    print(f"Cannot run the personal help viewer: {exc}", file=sys.stderr)
    return 127


def show_requested_help(
  page: str,
  arguments: Sequence[str],
  *,
  allow_all: bool = False,
  viewer: str | Path | None = None,
) -> int | None:
  """Return a help exit status, or None when normal script work should run."""
  if not arguments:
    return None
  first = arguments[0]
  if first not in EXTENDED_FLAGS and not (allow_all and first == "--all"):
    return None
  return call_pman(page, arguments, viewer)


def save_help(
  page: str,
  output: str | Path,
  *,
  view: str = "--all-help",
  extra: Sequence[str] = (),
  viewer: str | Path | None = None,
) -> int:
  """Return export status; the caller decides whether other work continues."""
  return call_pman(page, [view, "--save", str(output), *extra], viewer)
