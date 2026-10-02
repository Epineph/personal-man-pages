"""Export selected help, with optional Pandoc and LaTeX dependencies."""

from pathlib import Path
from contextlib import contextmanager, redirect_stderr
from datetime import datetime, timezone
import os
import shutil
import subprocess
import tempfile
import sys

from .document import HelpError


class DiagnosticTee:
  def __init__(self, terminal, log):
    self.terminal = terminal
    self.log = log

  def write(self, text: str) -> int:
    self.terminal.write(text)
    self.log.write(text)
    self.log.flush()
    return len(text)

  def flush(self) -> None:
    self.terminal.flush()
    self.log.flush()


@contextmanager
def export_log(path: Path | None, output: Path):
  """Append conversion diagnostics; stderr remains visible to the caller."""
  if path is None:
    yield None
    return
  if not path.parent.is_dir():
    raise HelpError(f"Log directory does not exist: {path.parent}")
  if path.resolve() == output.resolve():
    raise HelpError("The export and diagnostic log must use different paths.")
  with path.open("a", encoding="utf-8") as log:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.write(f"\n[{timestamp}] Exporting to {output}\n")
    log.flush()
    with redirect_stderr(DiagnosticTee(sys.stderr, log)):
      yield log


def save_document(
  text: str,
  title: str,
  output: Path,
  root: Path,
  resource_directory: Path,
  pdf_engine: str = "xelatex",
  force: bool = False,
) -> Path:
  """Stage exports beside their destination; preserve old files on failure."""
  suffix = output.suffix.casefold()
  if suffix not in {".md", ".html", ".pdf"}:
    raise HelpError("--save needs a filename ending in .md, .html or .pdf.")
  if not output.parent.is_dir():
    raise HelpError(f"Output directory does not exist: {output.parent}")
  if (output.exists() or output.is_symlink()) and not force:
    raise HelpError(f"Refusing to overwrite {output}; use --force if intended.")
  pandoc = None
  if suffix != ".md":
    pandoc = shutil.which("pandoc")
    if pandoc is None:
      raise HelpError(
        "Pandoc is not on PATH. HTML/PDF export requires Pandoc.\n"
        "Official installation guide: https://pandoc.org/installing.html\n"
        "Arch: sudo pacman -S pandoc\n"
        "Debian/Ubuntu: sudo apt-get install pandoc\n"
        "Markdown export (--save help.md) needs no additional package."
      )
    if suffix == ".pdf" and shutil.which(pdf_engine) is None:
      raise HelpError(
        f"PDF engine {pdf_engine!r} is not on PATH.\n"
        "PDF prerequisites: https://pandoc.org/installing.html\n"
        "For the default xelatex engine:\n"
        "Arch: sudo pacman -S texlive-xetex texlive-latexrecommended\n"
        "Debian/Ubuntu: sudo apt-get install texlive-xetex\n"
        "Alternatively select an installed engine with --pdf-engine."
      )

  with tempfile.TemporaryDirectory(
    prefix=".pman-export-", dir=output.parent
  ) as d:
    staged = Path(d) / ("help" + suffix)
    if suffix == ".md":
      staged.write_text(text, encoding="utf-8")
    else:
      command = [
        pandoc, "--from=markdown+tex_math_dollars", "--standalone",
        "--shift-heading-level-by=-1", "--metadata", f"title={title}",
        "--resource-path", os.pathsep.join([str(resource_directory), str(root)]),
        "--output", str(staged),
      ]
      if suffix == ".html":
        stylesheet = (root / "assets" / "export.css").read_text(encoding="utf-8")
        header = Path(d) / "style.html"
        header.write_text(f"<style>\n{stylesheet}\n</style>\n", encoding="utf-8")
        command += ["--to=html5", "--mathml", "--include-in-header", str(header)]
      else:
        command += [
          "--pdf-engine", pdf_engine, "-V", "geometry:margin=25mm",
          "-V", "fontsize:11pt", "-V", "papersize:a4",
          "-V", "colorlinks:true",
        ]
      # Pandoc supplies the title from metadata; remove the duplicate heading.
      body = text.split("\n", 1)[1].lstrip()
      completed = subprocess.run(
        command, input=body, text=True, encoding="utf-8",
        capture_output=True, check=False,
      )
      if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise HelpError(
          f"Pandoc export failed (exit {completed.returncode}).\n{detail}"
        )
      if not staged.is_file():
        raise HelpError("Pandoc exited successfully but produced no file.")
      if completed.stderr.strip():
        # Keep conversion warnings visible even after a successful export.
        print(completed.stderr.rstrip(), file=sys.stderr)

    if force:
      os.replace(staged, output)
    else:
      # Do not clobber a file created by another process during conversion.
      try:
        os.link(staged, output)
      except FileExistsError as exc:
        raise HelpError(f"Output appeared during export: {output}") from exc
  return output
