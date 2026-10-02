# Personal man-pages viewer

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`pman` reads personal command documentation, selects a help view and optionally
exports it for reading outside the terminal. Pages are ordinary Markdown files.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
pman PAGE [VIEW] [DISPLAY_OPTIONS]
pman PAGE [VIEW] --save PATH
pman PAGE [VIEW] --save-only PATH [--save-log LOG]
pman --list
pman --search TEXT
pman --new ID [--title TITLE] [--alias NAME]
```

Without a view flag, a selected page uses its practical long view. `--help`
describes the viewer's CLI. `--brief` selects a page's short help.

<!-- pman:section views views=long,detailed -->
## Help views

| Option | Meaning |
| --- | --- |
| `--brief` | Purpose and syntax |
| `--long-help` | Practical guide |
| `--detailed-help`, `--detailed` | Extended practical detail |
| `--technical-help` | Theory and implementation |
| `--list-examples` | Examples with context |
| `--all`, `--all-help` | Every section |
| `--section ID` | Select a section; may be repeated |

Use `--sections` to inspect section names and their view tags. A section's
heading, position and membership are maintained by the page author. Optional
views can be absent; `--all` always displays every authored section.

<!-- pman:section display views=long,detailed -->
## Rendering and paging

On a terminal, automatic rendering uses Glow when installed and plain Markdown
otherwise. A pager scrolls the result. `--paging never` disables it;
`--paging="never"` is equivalent. `--pager 'less -R'` overrides `$PAGER`; an
empty setting falls back to `less`. A missing fallback pager results in ordinary
printing. Output redirected to a file or pipe bypasses paging.

`--plain` forces Markdown. `--glow` forces Glow; `--ghow` is an alias. When
requested Glow is missing, an interactive session offers Markdown instead.
`--width N` controls Glow's wrapping; its default is capped at 81 columns.
`--paging auto` permits the fallback pager to skip a short page.

<!-- pman:section export views=long,detailed -->
## Export and local preview

`--save FILE.md` needs Python only. HTML and PDF require Pandoc on `PATH`.
PDF additionally requires the selected engine; XeLaTeX is the default. Use
`--pdf-engine lualatex`, `pdflatex` or `tectonic` for an installed alternative.
Additional LaTeX packages may be needed for a particular page.

`--save-only FILE` exports quietly; `--save FILE --save-only` also works. Normal
export prints the destination; `--show` additionally displays help. Errors remain
visible. `--save-log FILE` appends conversion diagnostics and status to a log.
Use `--force` to replace an existing export. Parent directories must exist.

Without quiet export, an export failure shows terminal help by default. Choose
`--on-error quit` to stop immediately. Failure still returns a nonzero status;
it never claims the export succeeded. A failed conversion leaves an old export
untouched. Dependencies are reported, never automatically installed.

HTML has embedded CSS and MathML for formulas. `--serve [PORT]` previews a saved
HTML file on localhost; `--open-browser` opens the printed URL. Only the saved
document is served. Ctrl-C stops the server, and the exported file remains.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Find pages and inspect a selected view:

```bash
pman --list
pman --search variance
pman zscore --technical-help --paging never
pman git-status --list-examples
```

Read two specific sections in their authored order:

```bash
pman zscore --sections
pman zscore --section theory --section worked-example
```

Save complete help for study, with conversion diagnostics:

```bash
pman zscore --all --save-only zscore.pdf --save-log zscore-export.log
```

Preview typeset mathematics in a browser:

```bash
pman zscore --technical-help --save zscore.html --serve --open-browser
```

Create and inspect a page:

```bash
pman --new tools.archive --title 'Archive wrapper' --alias archive
pman archive --path
pman --check
```

Use a different catalog without changing the working directory:

```bash
pman --home "$HOME/repos/personal-man-pages" zscore --all
```

Call the shell export helper after sourcing `integrations/pman.sh`:

```bash
pman_save_help demo.zscore zscore.html --all-help --save-only
```

<!-- pman:section catalog views=detailed -->
## Registry and page maintenance

`registry.json` uses schema 1 and a list of page entries. Each entry has `id`,
`title`, `summary`, `file`, and optionally `aliases`. IDs and aliases must be
unique and use lowercase letters, digits, dots, underscores or hyphens.
Page paths are relative to the catalog root and must stay inside that directory.

`--check` validates the registry and each page. It requires brief, long and
examples views; detailed and technical views are optional. It does not check
whether an independently maintained script still has the documented syntax.
`--new` generates a compact page and updates the registry. Edit its placeholders
and summary before relying on it. Simultaneous registry edits are not merged.

The catalog root comes from `--home`, then `PMAN_HOME`, then the checkout.
The installation symlink and registry IDs avoid assumptions about the user's
working directory or a script's location. Never use a moving basename as the
only help link when several scripts may have the same name.

<!-- pman:section internals views=technical -->
## Implementation and deliberate limits

The viewer uses Python's standard library. It interprets explicit section
comments rather than attempting a full Markdown parse. It preserves section
order, skips metadata parsing inside fenced code and rejects malformed markers.
Content is passed to external tools using argument arrays, not a shell.

Pandoc converts a selected Markdown snapshot. HTML uses MathML rather than an
online formula-rendering service. PDF uses a LaTeX engine. An export is staged
beside its destination and published only after conversion succeeds.

The preview server is local and serves one HTML document. It is not a public
web server or live Markdown editor. The templates have no live completion,
automatic argument extraction, package manager or traditional roff generator.

<!-- pman:section sources views=detailed -->
## External references

- [Glow documentation](https://github.com/charmbracelet/glow)
- [Pandoc manual](https://pandoc.org/MANUAL.html)
- [Pandoc installation](https://pandoc.org/installing.html)
- [GitHub mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)

References reviewed on 2026-10-02. Keep source links and version assumptions up
to date when adding native command guides.
