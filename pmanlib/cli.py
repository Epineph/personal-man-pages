"""Command-line entry point for selective, personal help pages."""

from pathlib import Path
import argparse
import os
import shutil
import sys

from . import __version__
from .catalog import Catalog
from .document import HelpError, read_document
from .export import export_log, save_document
from .render import display
from .serve import serve_html


# ----- Arguments ---------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="pman",
    description="Read personal Markdown help by stable page ID or alias.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Examples:
  pman zscore --long-help
  pman zscore --technical-help
  pman git-status --list-examples
  pman zscore --all --plain > zscore-help.md
  pman --new tools.archive --title 'Archive wrapper' --alias archive

Use pman --long-help for the viewer's extended manual.
--help describes the viewer; --brief selects a page's short help.""",
    allow_abbrev=False,
  )
  parser.add_argument("page", nargs="?", help="registered ID or alias")
  parser.add_argument("--version", action="version", version=__version__)
  parser.add_argument(
    "--home", type=Path, help="catalog root (default: PMAN_HOME or checkout)"
  )
  views = parser.add_mutually_exclusive_group()
  for flags, view, explanation in [
    (("--brief",), "brief", "short purpose, syntax and help choices"),
    (("--long-help",), "long", "practical guide (default page view)"),
    (("--detailed-help", "--detailed"), "detailed", "extended practical detail"),
    (("--technical-help",), "technical", "theory and implementation details"),
    (("--all", "--all-help"), "all", "every section, including theory"),
    (("--list-examples",), "examples", "examples and their explanations only"),
  ]:
    views.add_argument(
      *flags, dest="view", action="store_const", const=view, help=explanation
    )
  views.add_argument(
    "--section", action="append", metavar="ID", help="select a section; repeat"
  )
  actions = parser.add_mutually_exclusive_group()
  actions.add_argument("--list", action="store_true", help="list page IDs")
  actions.add_argument("--search", metavar="TEXT", help="search pages and names")
  actions.add_argument("--check", action="store_true", help="validate all pages")
  actions.add_argument("--path", action="store_true", help="print a page's path")
  actions.add_argument(
    "--sections", action="store_true", help="list section IDs and view tags"
  )
  actions.add_argument("--new", metavar="ID", help="create and register a page")
  parser.add_argument("--title", help="title for --new (defaults to the ID)")
  parser.add_argument(
    "--alias", action="append", default=[], help="alias for --new; repeat"
  )
  renderers = parser.add_mutually_exclusive_group()
  renderers.add_argument(
    "--renderer", choices=("auto", "plain", "glow"), default="auto"
  )
  renderers.add_argument(
    "--plain", dest="renderer", action="store_const", const="plain",
    help="emit Markdown without Glow",
  )
  renderers.add_argument(
    "--glow", "--ghow", dest="renderer", action="store_const", const="glow",
    help="use Glow; offer Markdown if missing in an interactive terminal",
  )
  parser.add_argument(
    "--paging", choices=("always", "auto", "never"), default="always",
    help="paging policy (default: always; redirected output is never paged)",
  )
  parser.add_argument(
    "--no-pager", dest="paging", action="store_const", const="never",
    help="alias for --paging never",
  )
  parser.add_argument(
    "--pager", metavar="COMMAND",
    help="pager command (default: $PAGER, then less); quote any arguments",
  )
  parser.add_argument(
    "--width", type=int, default=min(81, shutil.get_terminal_size().columns),
    help="Glow wrap width (default: terminal width, capped at 81)",
  )
  parser.add_argument(
    "--save", type=Path, metavar="PATH",
    help="save selected help as .md, .html or .pdf instead of displaying it",
  )
  parser.add_argument(
    "--save-only", nargs="?", const=True, type=Path, metavar="PATH",
    help="quiet export: provide PATH here, or combine with --save PATH",
  )
  parser.add_argument(
    "--save-log", type=Path, metavar="PATH",
    help="append export status and conversion diagnostics to a UTF-8 log",
  )
  parser.add_argument(
    "--force", action="store_true", help="allow --save to replace an export"
  )
  parser.add_argument(
    "--pdf-engine", default="xelatex",
    choices=("xelatex", "lualatex", "pdflatex", "tectonic"),
    help="Pandoc PDF engine (default: xelatex)",
  )
  parser.add_argument(
    "--show", action="store_true", help="also display help after --save"
  )
  parser.add_argument(
    "--on-error", choices=("continue", "quit"), default="continue",
    help="after export failure, show help or quit (default: continue)",
  )
  parser.add_argument(
    "--serve", nargs="?", const=8000, type=int, metavar="PORT",
    help="serve saved HTML on 127.0.0.1 (default port: 8000; 0: free port)",
  )
  parser.add_argument(
    "--open-browser", action="store_true",
    help="open the --serve URL in a browser",
  )
  return parser


def list_pages(catalog: Catalog, query: str | None = None) -> int:
  found = []
  for page in catalog.pages:
    metadata = " ".join([
      page.identifier, page.title, page.summary, *page.aliases
    ])
    if query is not None:
      metadata += "\n" + read_document(page.path).select("all")
      if query.casefold() not in metadata.casefold():
        continue
    found.append(page)
  if not found:
    print("No matching pages.")
    return 1
  width = max(len(page.identifier) for page in found)
  for page in sorted(found, key=lambda item: item.identifier):
    print(f"{page.identifier:<{width}}  {page.summary}")
    if page.aliases:
      print(f"{'':<{width}}  Aliases: {', '.join(page.aliases)}")
  return 0


def run(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  quiet_export = args.save_only is not None
  if isinstance(args.save_only, Path):
    if args.save is not None:
      parser.error("specify the output with --save or --save-only, not both")
    args.save = args.save_only
  if quiet_export and args.save is None:
    parser.error("--save-only requires PATH or --save PATH")
  if quiet_export and (args.show or args.serve is not None):
    parser.error("--save-only cannot be combined with --show or --serve")
  if args.save_log is not None and args.save is None:
    parser.error("--save-log requires --save or --save-only")
  if args.width < 20:
    parser.error("--width must be at least 20")
  if (args.title is not None or args.alias) and args.new is None:
    parser.error("--title and --alias require --new")
  if args.force and args.save is None:
    parser.error("--force requires --save")
  if args.show and args.save is None:
    parser.error("--show requires --save")
  if args.open_browser and args.serve is None:
    parser.error("--open-browser requires --serve")
  if args.serve is not None:
    if args.save is None or args.save.suffix.casefold() != ".html":
      parser.error("--serve requires --save FILE.html")
    if not 0 <= args.serve <= 65535:
      parser.error("--serve port must be between 0 and 65535")
  global_action = args.list or args.check or args.new is not None
  global_action = global_action or args.search is not None
  if global_action and (args.page is not None or args.view or args.section):
    parser.error("catalog actions cannot be combined with a page or help view")
  if (args.path or args.sections) and (args.view or args.section):
    parser.error("--path/--sections cannot be combined with a help view")
  page_action = args.path or args.sections
  if args.save is not None and (global_action or page_action):
    parser.error("--save cannot be combined with a catalog/path/section listing")
  if page_action and args.page is None:
    parser.error("--path/--sections require a page")
  if (
    not global_action and args.page is None and not args.view
    and not args.section and args.save is None
  ):
    parser.print_help()
    return 0

  root = args.home or Path(
    os.environ.get("PMAN_HOME", str(Path(__file__).resolve().parents[1]))
  )
  catalog = Catalog(root)
  if args.list or args.search is not None:
    return list_pages(catalog, args.search)
  if args.new is not None:
    path = catalog.create(args.new, args.title or args.new, args.alias)
    print(f"Created {path}\nEdit the page and its registry summary, then run:")
    print(f"  pman --home {str(catalog.root)!r} --check")
    return 0
  if args.check:
    failures = []
    for page in catalog.pages:
      try:
        document = read_document(page.path)
        for required in ("brief", "long", "examples"):
          document.select(required)
      except HelpError as exc:
        failures.append(f"{page.identifier}: {exc}")
    if failures:
      for failure in failures:
        print(failure, file=sys.stderr)
      return 2
    print(
      f"Valid: {len(catalog.pages)} page(s), identifiers and aliases unique."
    )
    return 0

  page = catalog.resolve(args.page or "pman")
  if args.path:
    print(page.path)
    return 0
  document = read_document(page.path)
  if args.sections:
    for section in document.sections:
      print(
        f"{section.identifier}: {section.heading} "
        f"[{','.join(section.views)}]"
      )
    return 0
  text = document.select(args.view or "long", args.section)
  if args.save is not None:
    output = args.save.expanduser().absolute()
    protected = {catalog.registry_path, *(p.path for p in catalog.pages)}
    if output.resolve() in protected:
      raise HelpError("Choose an export path outside the source help files.")
    log_path = args.save_log.expanduser().absolute() if args.save_log else None
    if log_path and log_path.resolve() in protected:
      raise HelpError("Choose a log path outside the source help files.")
    saved = None
    with export_log(log_path, output) as log:
      try:
        saved = save_document(
          text, page.title, output, catalog.root, page.path.parent,
          args.pdf_engine, args.force,
        )
      except (HelpError, OSError, UnicodeError) as exc:
        print(f"pman: Export failed: {exc}", file=sys.stderr)
      if saved is not None:
        message = f"Saved {saved}"
        if log is not None:
          log.write(message + "\n")
        if not quiet_export:
          print(message)
    if saved is None:
      if args.on_error == "continue" and not quiet_export:
        print("pman: Continuing with terminal help.", file=sys.stderr)
        display(text, args.renderer, args.paging, args.pager, args.width)
      return 2
    if args.show:
      status = display(text, args.renderer, args.paging, args.pager, args.width)
      if status:
        return status
    if args.serve is not None:
      return serve_html(saved, args.serve, args.open_browser)
    return 0
  return display(text, args.renderer, args.paging, args.pager, args.width)


def main(argv: list[str] | None = None) -> int:
  try:
    return run(argv)
  except BrokenPipeError:
    return 0
  except (HelpError, OSError, UnicodeError) as exc:
    print(f"pman: {exc}", file=sys.stderr)
    return 2
  except KeyboardInterrupt:
    return 130
