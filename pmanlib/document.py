"""Select help sections without interpreting or executing Markdown contents."""

from dataclasses import dataclass
from pathlib import Path
import re


# ----- Page format -------------------------------------------------------------

VIEWS = frozenset({"brief", "long", "detailed", "technical", "examples"})
IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
MARKER = re.compile(
  r"<!-- pman:section ([a-z0-9][a-z0-9._-]*) "
  r"views=([a-z,]+) -->\s*\Z"
)
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)\Z")


class HelpError(ValueError):
  """An actionable page, registry, or rendering error."""


@dataclass(frozen=True)
class Section:
  identifier: str
  views: tuple[str, ...]
  text: str

  @property
  def heading(self) -> str:
    return self.text.splitlines()[0].removeprefix("## ")


@dataclass(frozen=True)
class Document:
  preamble: str
  sections: tuple[Section, ...]

  def select(
    self, view: str = "long", identifiers: list[str] | None = None
  ) -> str:
    """Preserve author order; never substitute an unrelated help view."""
    if identifiers:
      available = {section.identifier for section in self.sections}
      missing = set(identifiers) - available
      if missing:
        raise HelpError("Unknown section(s): " + ", ".join(sorted(missing)))
      selected = [s for s in self.sections if s.identifier in identifiers]
    elif view == "all":
      selected = list(self.sections)
    elif view in VIEWS:
      selected = [s for s in self.sections if view in s.views]
    else:
      raise HelpError(f"Unknown help view: {view}")
    if not selected:
      raise HelpError(
        f"This page has no {view!r} view. Use --sections or --all."
      )
    pieces = [self.preamble, *(section.text for section in selected)]
    return "\n\n".join(pieces).rstrip() + "\n"


def parse_document(text: str, source: str = "page") -> Document:
  """Read explicit section markers, ignoring markers inside fenced code."""
  preamble: list[str] = []
  sections: list[Section] = []
  body: list[str] = []
  current: tuple[str, tuple[str, ...]] | None = None
  fence: str | None = None

  def finish() -> None:
    if current is None:
      return
    contents = "\n".join(body).strip()
    if not contents.startswith("## "):
      raise HelpError(
        f"{source}: section {current[0]!r} must start with '## Heading'."
      )
    sections.append(Section(current[0], current[1], contents))

  for number, line in enumerate(text.splitlines(), 1):
    # The closing fence must use the same character and sufficient length.
    if fence is not None:
      destination = body if current is not None else preamble
      destination.append(line)
      closing = re.fullmatch(r" {0,3}([`~]+)\s*", line)
      if closing:
        token = closing.group(1)
        if set(token) == {fence[0]} and len(token) >= len(fence):
          fence = None
      continue

    opening = FENCE.fullmatch(line)
    if opening:
      fence = opening.group(1)
      (body if current is not None else preamble).append(line)
      continue

    match = MARKER.fullmatch(line)
    if match:
      finish()
      views = tuple(match.group(2).split(","))
      if len(set(views)) != len(views) or set(views) - VIEWS:
        raise HelpError(f"{source}:{number}: invalid or duplicate view tags.")
      current = (match.group(1), views)
      body = []
    else:
      if "<!-- pman:" in line:
        raise HelpError(f"{source}:{number}: malformed section marker.")
      (body if current is not None else preamble).append(line)

  if fence is not None:
    raise HelpError(f"{source}: unclosed fenced code block.")
  finish()
  title = "\n".join(preamble).strip()
  # Keeping the preamble title-only prevents theory leaking into examples.
  if not re.fullmatch(r"# [^\n]+", title):
    raise HelpError(f"{source}: start with exactly one '# Title' line.")
  if not sections:
    raise HelpError(f"{source}: no pman sections found.")
  names = [s.identifier for s in sections]
  if len(names) != len(set(names)):
    raise HelpError(f"{source}: section identifiers must be unique.")
  return Document(title, tuple(sections))


def read_document(path: Path) -> Document:
  try:
    return parse_document(path.read_text(encoding="utf-8"), str(path))
  except (OSError, UnicodeError) as exc:
    raise HelpError(f"Cannot read {path}: {exc}") from exc
