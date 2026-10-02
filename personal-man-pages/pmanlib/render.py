"""Display Markdown locally; keep redirected output suitable for saving."""

from pathlib import Path
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

from .document import HelpError


def display(
  text: str,
  renderer: str = "auto",
  paging: str = "always",
  pager_command: str | None = None,
  width: int = 81,
) -> int:
  """Prefer Glow on a terminal, otherwise use Markdown and an optional pager."""
  terminal = sys.stdout.isatty()
  use_pager = terminal and sys.stdin.isatty() and paging != "never"
  glow = shutil.which("glow")
  if renderer == "glow" and glow is None:
    print(
      "pman: Glow is not on PATH. Get it from "
      "https://github.com/charmbracelet/glow#installation", file=sys.stderr,
    )
    if sys.stdin.isatty():
      try:
        answer = input("Display plain Markdown instead? [Y/n] ").strip().lower()
      except EOFError:
        answer = "n"
      if answer in {"", "y", "yes"}:
        renderer = "plain"
      else:
        raise HelpError("Glow display cancelled.")
    else:
      raise HelpError("Use --plain to display help without Glow.")
  use_glow = renderer == "glow" or (
    renderer == "auto" and terminal and glow is not None
  )
  if not use_glow and not use_pager:
    sys.stdout.write(text)
    return 0

  # Pass a file rather than stdin so a pager can still read keyboard input.
  with tempfile.TemporaryDirectory(prefix="pman-") as directory:
    path = Path(directory) / "help.md"
    path.write_text(text, encoding="utf-8")
    if use_glow:
      # Render first, then page the result ourselves for a consistent --pager.
      command = [glow, "-w", str(width), "--pager=false", str(path)]
      environment = dict(os.environ)
      if terminal:
        environment.setdefault("CLICOLOR_FORCE", "1")
      completed = subprocess.run(
        command, check=False, capture_output=True, text=True,
        encoding="utf-8", env=environment,
      )
      status = completed.returncode
      if completed.stderr:
        sys.stderr.write(completed.stderr)
      if status == 0 or renderer == "glow":
        if status != 0:
          return status
        text = completed.stdout
        path.write_text(text, encoding="utf-8")
        if not use_pager:
          sys.stdout.write(text)
          return 0
      else:
        print("pman: Glow failed; displaying Markdown instead.", file=sys.stderr)

    if use_pager:
      pager_setting = (
        pager_command if pager_command is not None
        else os.environ.get("PAGER", "")
      ).strip()
      try:
        command = shlex.split(pager_setting) if pager_setting else []
      except ValueError as exc:
        raise HelpError(f"Invalid PAGER quoting: {exc}") from exc
      if not command and shutil.which("less"):
        command = ["less", "-R", "-X"]
        if paging == "auto":
          command.append("-F")
      if command:
        if shutil.which(command[0]) is None:
          raise HelpError(f"Pager executable not found: {command[0]}")
        return subprocess.run([*command, str(path)], check=False).returncode
    sys.stdout.write(text)
    return 0
