"""Resolve stable identifiers and aliases through a small JSON registry."""

from dataclasses import dataclass
from pathlib import Path
import json
import os
import tempfile

from .document import HelpError, IDENTIFIER, parse_document


# ----- Registry loading and validation ----------------------------------------

@dataclass(frozen=True)
class Page:
  identifier: str
  title: str
  summary: str
  aliases: tuple[str, ...]
  path: Path


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
  result: dict = {}
  for key, value in pairs:
    if key in result:
      raise HelpError(f"Duplicate JSON key: {key}")
    result[key] = value
  return result


class Catalog:
  def __init__(self, root: Path):
    self.root = root.expanduser().resolve()
    self.registry_path = self.root / "registry.json"
    try:
      self.data = json.loads(
        self.registry_path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_keys,
      )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
      raise HelpError(f"Cannot read {self.registry_path}: {exc}") from exc
    self.pages, self.names = self.validate(self.data)

  def validate(self, data: object) -> tuple[tuple[Page, ...], dict[str, Page]]:
    if not isinstance(data, dict) or type(data.get("schema")) is not int:
      raise HelpError("registry.json requires an integer 'schema' field.")
    if data["schema"] != 1 or not isinstance(data.get("pages"), list):
      raise HelpError("registry.json requires schema 1 and a 'pages' array.")
    pages: list[Page] = []
    names: dict[str, Page] = {}
    paths: set[Path] = set()
    for entry in data["pages"]:
      if not isinstance(entry, dict):
        raise HelpError("Each registry entry must be an object.")
      for field in ("id", "title", "summary", "file"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip() or "\n" in value:
          raise HelpError(f"Each page needs a nonempty, single-line {field!r}.")
      identifier = entry["id"]
      aliases = entry.get("aliases", [])
      if not isinstance(aliases, list) or not all(
        isinstance(alias, str) for alias in aliases
      ):
        raise HelpError(f"{identifier}: aliases must be an array of strings.")
      for name in [identifier, *aliases]:
        if not IDENTIFIER.fullmatch(name):
          raise HelpError(f"Invalid identifier or alias: {name!r}")
      relative = Path(entry["file"])
      path = (self.root / relative).resolve()
      if relative.is_absolute() or not path.is_relative_to(self.root):
        raise HelpError(f"{identifier}: the page must stay inside PMAN_HOME.")
      if path.suffix != ".md":
        raise HelpError(f"{identifier}: the page must be a Markdown (.md) file.")
      if path in paths:
        raise HelpError(f"More than one registry entry points to {path}.")
      paths.add(path)
      page = Page(
        identifier, entry["title"], entry["summary"], tuple(aliases), path
      )
      for name in [identifier, *aliases]:
        if name in names:
          raise HelpError(f"Duplicate identifier or alias: {name!r}")
        names[name] = page
      pages.append(page)
    return tuple(pages), names

  def resolve(self, name: str) -> Page:
    try:
      return self.names[name]
    except KeyError as exc:
      raise HelpError(f"Unknown page {name!r}. Use pman --list.") from exc

  def create(self, identifier: str, title: str, aliases: list[str]) -> Path:
    """Create a compact page; validate before changing the registry."""
    if not IDENTIFIER.fullmatch(identifier):
      raise HelpError("Use lowercase letters, digits, dots, '_' or '-' in IDs.")
    relative = f"pages/{identifier}.md"
    candidate = dict(self.data)
    candidate["pages"] = [*self.data["pages"], {
      "id": identifier,
      "title": title,
      "summary": "Describe what this command does.",
      "aliases": aliases,
      "file": relative,
    }]
    self.validate(candidate)
    path = self.root / relative
    template = (self.root / "templates" / "compact.md").read_text(
      encoding="utf-8"
    )
    template = template.replace("{{TITLE}}", title).replace("{{ID}}", identifier)
    parse_document(template, str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
      with path.open("x", encoding="utf-8") as handle:
        handle.write(template)
    except FileExistsError as exc:
      raise HelpError(f"Refusing to overwrite {path}.") from exc
    temporary: str | None = None
    try:
      with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=self.root, delete=False
      ) as handle:
        temporary = handle.name
        json.dump(candidate, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
      os.replace(temporary, self.registry_path)
    except OSError:
      path.unlink(missing_ok=True)
      raise
    finally:
      if temporary is not None:
        Path(temporary).unlink(missing_ok=True)
    self.data = candidate
    self.pages, self.names = self.validate(candidate)
    return path
