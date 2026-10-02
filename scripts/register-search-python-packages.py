#!/usr/bin/env python3
"""Merge the help entry and optionally install a user-level command wrapper."""

from pathlib import Path
import argparse
import json
import os
import shutil
import sys
import tempfile


# ----- Arguments ---------------------------------------------------------------

def main() -> int:
  parser = argparse.ArgumentParser(
    description=(
      "Register search-python-packages in an existing personal-man-pages repo."
    ),
    epilog=(
      "Example: python3 scripts/register-search-python-packages.py "
      "--install-wrapper\n"
      "The original /usr/local/bin/search-python-packages remains the delegate."
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    allow_abbrev=False,
  )
  parser.add_argument(
    "--home", type=Path, default=Path(__file__).resolve().parents[1],
    help="repository root (default: this script's checkout)",
  )
  parser.add_argument(
    "--install-wrapper", action="store_true",
    help="link the wrapper into ~/.local/bin",
  )
  parser.add_argument(
    "--bin-dir", type=Path, default=Path.home() / ".local" / "bin",
    help="wrapper link directory (default: ~/.local/bin)",
  )
  args = parser.parse_args()
  root = args.home.expanduser().resolve()
  sys.path.insert(0, str(root))
  try:
    from pmanlib.catalog import Catalog
    from pmanlib.document import HelpError, read_document
  except ImportError as exc:
    parser.error(f"--home must contain the personal-man-pages viewer: {exc}")

  # ----- Validate before writing or creating an installation link --------------

  catalog = Catalog(root)
  entry_path = root / "entries" / "search-python-packages.json"
  entry = json.loads(entry_path.read_text(encoding="utf-8"))
  entries = catalog.data["pages"]
  current = next((p for p in entries if p["id"] == entry["id"]), None)
  if current is not None and current != entry:
    raise HelpError(
      "This stable ID already has a different entry. Merge it manually; "
      "no registry change was made."
    )
  candidate = dict(catalog.data)
  candidate["pages"] = entries if current else [*entries, entry]
  catalog.validate(candidate)
  document = read_document(root / entry["file"])
  for view in ("brief", "long", "detailed", "technical", "examples"):
    document.select(view)

  wrapper = root / "wrappers" / "search-python-packages"
  destination = args.bin_dir.expanduser().absolute() / wrapper.name
  if args.install_wrapper:
    if not wrapper.is_file():
      raise HelpError(f"Wrapper file is missing: {wrapper}")
    occupied = destination.exists() or destination.is_symlink()
    if occupied and (
      not destination.is_symlink() or destination.resolve() != wrapper
    ):
      raise HelpError(f"Refusing to replace an unrelated path: {destination}")

  # ----- Merge the entry, preserving unrelated pages ---------------------------

  if current is None:
    temporary = None
    try:
      with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=root, delete=False
      ) as handle:
        temporary = Path(handle.name)
        json.dump(candidate, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
      shutil.copymode(catalog.registry_path, temporary)
      os.replace(temporary, catalog.registry_path)
    finally:
      if temporary is not None:
        temporary.unlink(missing_ok=True)
    print(f"Registered {entry['id']} -> {entry['file']}")
  else:
    print(f"Already registered: {entry['id']}")

  # ----- Optional user-level link ----------------------------------------------

  if args.install_wrapper:
    wrapper.chmod(wrapper.stat().st_mode | 0o111)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.is_symlink():
      destination.symlink_to(wrapper)
    print(f"Wrapper link: {destination}")
    print("Place that directory before /usr/local/bin in PATH.")
  print("Read it with: pman search-python-packages --long-help")
  return 0


if __name__ == "__main__":
  try:
    raise SystemExit(main())
  except (OSError, ValueError) as exc:
    print(f"Registration failed: {exc}", file=sys.stderr)
    raise SystemExit(2)
