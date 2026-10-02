# Personal man-pages

Personal, selective command documentation written in Markdown. Keep routine
help short, put practical guidance in a longer view, and put mathematical or
implementation detail in a separate technical view.

This is a repository starter. It includes a working viewer, a small registry,
editable pages, export helpers and examples of script/function integration.
The core needs **Python 3.10 or newer**, with no third-party Python packages.

## Start here

Extract this folder into a permanent location, for example
`~/repos/personal-man-pages`, then run:

```bash
cd ~/repos/personal-man-pages
python3 bin/pman --check
python3 bin/pman zscore --technical-help --paging never
bash scripts/install.sh
```

Installation creates `~/.local/bin/pman` as a symlink to this checkout. Keep the
checkout in place. Page edits take effect immediately, without reinstalling.
If `~/.local/bin` is absent from your shell's `PATH`, add this line to `.zshrc`
or `.bashrc` once and start a new shell:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

You can keep using `python3 bin/pman` without installing anything. Run example
scripts with `bash examples/greet.sh` and `python3 examples/zscore.py`.

Remove only this checkout's installation link with:

```bash
bash scripts/install.sh --uninstall
```

## What each help view means

| Flag | Content |
| --- | --- |
| `--help` | The viewer's ordinary CLI help |
| `--brief` | A selected page's short purpose and syntax |
| `--long-help` | Practical guide; the default when a page is supplied |
| `--detailed-help`, `--detailed` | More practical detail and limitations |
| `--technical-help` | Mathematics, assumptions or implementation details |
| `--list-examples` | Examples and their explanations |
| `--all`, `--all-help` | Every section, including technical material |
| `--section ID` | A particular section; repeat to select several |

`pman --long-help` selects the viewer's own manual. In integrated scripts,
ordinary `--help` stays native and advertises the extra views. Only an explicit
leading extended-help flag is intercepted.

```bash
pman --list
pman --search variance
pman zscore --list-examples
pman zscore --sections
pman zscore --section theory --section worked-example
pman git-status --long-help
```

A page need not have every view. Missing optional views produce a clear error,
without silently substituting unrelated content. The repository check requires
only brief help, practical long help and examples.

## Paging and terminal rendering

Paging is enabled in interactive terminals by default. Redirected output is
unpaged Markdown. If Glow is installed, automatic terminal rendering uses it;
otherwise the viewer displays plain Markdown.

```bash
pman zscore --all --paging never
pman zscore --all --paging="never"
pman zscore --all --pager 'less -R'
pman zscore --all --plain
pman zscore --all --glow
```

`--pager COMMAND` overrides `$PAGER`; an empty setting falls back to `less`.
Quote arguments as one value. Pager commands are split into an argument array,
not evaluated by a shell; shell pipelines and redirections are not supported.
If no pager is available, help prints normally. `--paging auto` lets the fallback
`less` exit immediately when the page fits on one screen.

`--ghow` is accepted as an alias for `--glow`. If explicit Glow rendering is
requested but Glow is missing, an interactive session offers plain Markdown.
Noninteractive use reports the missing executable and returns a nonzero status.
No dependency is installed automatically.

The pager provides scrolling; Glow's separate directory-browsing TUI is not
used. Terminal output does not typeset LaTeX formulas. Use HTML or PDF for that.

## Save help for study

`--save PATH` exports the selected view. The filename extension determines the
format. Bare filenames go into the current working directory. Parent directories
must already exist; existing exports are protected unless `--force` is supplied.

```bash
pman zscore --all --save zscore.md
pman zscore --technical-help --save zscore.html
pman zscore --technical-help --save zscore.pdf
pman zscore --all --save-only zscore.pdf --save-log zscore-export.log
pman zscore --all --save zscore.md --save-only
pman zscore --all --save zscore.html --force --show
```

| Format | Required tools | Result |
| --- | --- | --- |
| `.md` | Python only | Selected Markdown, without section metadata |
| `.html` | Pandoc | Standalone HTML, embedded CSS and MathML mathematics |
| `.pdf` | Pandoc and a LaTeX engine | A4 PDF; XeLaTeX is the default |

HTML mathematics uses Pandoc's `--mathml` output. The supplied examples need no
online math service, external stylesheet or JavaScript. Modern browsers render
MathML; complex LaTeX macros may require adaptation. User-added remote images
or links retain their own requirements. PDF conversion exposes Pandoc's errors
for missing fonts or LaTeX packages.

`--save-only FILE` suppresses normal terminal output and never falls back to
displaying the page. It can also be written `--save FILE --save-only`.
Errors remain on stderr. `--save-log FILE` appends timestamps, export status and
conversion diagnostics; the help content is in the export, not in this log.
It does not capture unrelated work done by the calling script.

Without `--save-only`, failed exports default to showing the selected help in
the terminal. `--on-error quit` disables that fallback. Either way, failure
returns a nonzero status and does not replace an existing export. Successful
exports print the output path; add `--show` to also read the page immediately.

Pandoc or a missing PDF engine is checked only when that format is requested.
Errors include installation hints and the
[official Pandoc installation guide](https://pandoc.org/installing.html).

## Local HTML preview

```bash
pman zscore --technical-help --save zscore.html --serve --open-browser
pman zscore --all --save zscore.html --force --serve 8765
```

The server binds to `127.0.0.1`, serves the exported document only, and stops
with Ctrl-C. Default port: 8000; `--serve 0` asks for a free port. The console
prints the URL. `--open-browser` requests opening it with the system browser.
The saved file remains after the server stops. You can also open that HTML file
directly in a browser. This preview is a saved snapshot, not a live editor.

## How commands link to their pages

The registry supplies a stable ID and optional convenient aliases:

```json
{
  "id": "tools.archive",
  "title": "Archive wrapper",
  "summary": "Create encrypted archives with progress reporting.",
  "aliases": ["archive", "r7z"],
  "file": "pages/archive.md"
}
```

A script requests `tools.archive`. `pman` resolves the current page location.
Move the page by editing `file`; rename the command by adding/changing aliases.
Keep the stable ID unless you also update the scripts that refer to it.
No GitHub URL, absolute script pathname or basename matching is necessary.

`pman archive --path` prints the underlying Markdown path. Set `PMAN_HOME` or
use `--home DIRECTORY` to choose a different catalog root. The precedence is
`--home`, then `PMAN_HOME`, then the viewer's checkout; the working directory
does not determine which help registry is loaded.

## Add and adapt a page

```bash
pman --new tools.archive --title 'Archive wrapper' --alias archive --alias r7z
pman archive --path
pman --check
```

Edit the generated page and its summary in `registry.json`. The starter text is
deliberately marked as instructions to replace. Section headings and identifiers
are yours; view tags decide where a section appears:

```markdown
<!-- pman:section options views=long,detailed -->
## Options worth knowing

Explain defaults and the options that matter for this command.
```

Each page starts with exactly one `# Title`, followed by tagged `##` sections.
HTML comments are invisible in normal GitHub Markdown rendering. Tags inside
fenced code blocks are treated as examples, not metadata. `--all` includes every
section in its authored order. A shared section can have several view tags.

`templates/compact.md` suits small utilities. Append a technical section from
`templates/technical-section.md` only when it helps. State important operational
constraints in practical help too; users should not need theory to use a tool.
For native commands, add source links, a review date and version assumptions.

## Integrate Bash, Zsh or Python

The working examples are in `examples/`. The common shell adapter can be
sourced from a script or from `.zshrc`/`.bashrc`:

```bash
source "$HOME/repos/personal-man-pages/integrations/pman.sh"

function my_command {
  if pman_is_help_request "$@"; then
    pman_show_help tools.archive "$@"
    return $?
  fi
  # Put this help branch before the command's existing work.
}

pman_save_help tools.archive "$HOME/archive-help.pdf" --all-help --save-only
```

For an executable script, exit with the help status instead of `return`.
The common adapter leaves `--all` available for the script's ordinary purpose;
enable it explicitly only when it does not conflict. `--all-help` always names
the complete help view. Native commands can be documented through `pman`
without wrapping or replacing them.

For Python, copy `integrations/pman_help.py` beside the script or add its directory
to the import path. The numerical example demonstrates the latter approach.

```python
from pman_help import show_requested_help, save_help
import sys

status = show_requested_help("tools.archive", sys.argv[1:])
if status is not None:
  raise SystemExit(status)

# Ordinary work goes after the help check.
# A separate export call returns a status without exiting the caller:
status = save_help("tools.archive", "archive-help.html")
```

`PMAN_BIN` can name the viewer executable for adapters. It is one executable
path, not a shell command containing additional arguments. Keep each script's
short native help and its page syntax in agreement; these are maintained
explicitly rather than extracted automatically from arbitrary code.

## Packages

Only install the optional tools for features you want.

**Arch Linux**:

```bash
sudo pacman -S python git less
sudo pacman -S glow
sudo pacman -S pandoc texlive-xetex texlive-latexrecommended
sudo pacman -S github-cli
```

**Debian/Ubuntu**:

```bash
sudo apt-get update
sudo apt-get install python3 git less
sudo apt-get install pandoc texlive-xetex
sudo apt-get install gh
```

For Glow on Debian/Ubuntu, follow its
[official installation instructions](https://github.com/charmbracelet/glow#installation);
availability in distro repositories varies. Its release page also provides
Linux packages. A distro's Python must be 3.10 or newer.

**Fedora** (core and HTML export):

```bash
sudo dnf install python3 git less pandoc
```

The Python viewer and Pandoc command construction use portable standard-library
APIs. Installation and shell examples target Linux with Bash/Zsh. Windows
installation and PowerShell adapters are left for a focused follow-up.

## Put this starter on GitHub

From the extracted folder, after reviewing the files:

```bash
git init -b main
git add .
git commit -m 'Start personal Markdown help pages'
gh auth login
gh repo create personal-man-pages --private --source=. --remote=origin --push
```

This creates a private repository under the authenticated account. Choose
`--public` instead if that is what you want. If the repository already exists,
add its remote and push rather than running `gh repo create`. See the
[official GitHub CLI manual](https://cli.github.com/manual/gh_repo_create).
No GitHub repository has been created by preparing these files.

## Layout and checks

| Path | Role |
| --- | --- |
| `bin/pman` | Checkout-aware launcher |
| `pmanlib/` | Registry, section selection, display, export and preview |
| `registry.json` | Stable page IDs and aliases |
| `pages/` | Editable personal documentation |
| `templates/` | Compact page and optional technical section |
| `integrations/` | Callable shell and Python help/export helpers |
| `examples/` | Complete Bash, Python and shell-function examples |
| `assets/export.css` | Embedded HTML styling and print layout |
| `scripts/install.sh` | User-level symlink installation/removal |
| `tests/` | Behavior checks for selection, integration and export |
| `.github/workflows/` | Python and page checks for future pushes |

```bash
python3 bin/pman --check
python3 -m unittest discover -s tests -v
```

The viewer returns 0 for success, 1 for an empty search/list result, and 2 for
its validation/export errors. An external renderer or pager's failure status is
propagated. Ctrl-C during reading returns 130; stopping a preview returns 0.

The prepared starter passed 17 behavior checks on Python 3.12, including Bash
and Zsh function integration. Real HTML/PDF conversion, localhost preview and
installation/removal were checked separately. Glow was unavailable during
verification; test its rendering on your own installation. The CI matrix has
been supplied for future GitHub runs, rather than executed here.

Follow-up work can add completion, a package installer, more native command
pages or traditional `man` output. They are not required to start maintaining
and using this repository.
