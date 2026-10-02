# Search Python packages

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`search-python-packages` searches PyPI project names, retrieves metadata and
recent download counts for a bounded set of candidates, and displays results
in a Rich table. It can compare names with conda-forge, export the results and
prompt to install selected packages with pip.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
search-python-packages KEYWORD [KEYWORD ...] [SEARCH_OPTIONS]
search-python-packages --long-help
search-python-packages --list-examples
pman search-python-packages --all
```

Use native `--help` for the complete parser's accepted values and defaults.
Put a personal-help view first, then any viewer options. `--all-help` selects
the whole page through the wrapper; its ordinary `--all` is not intercepted.

<!-- pman:section workflow views=long,detailed -->
## Search workflow

The supplied excerpt joins the keywords into a query label and selects matching
project names. If there are no exact name matches, it may provide fuzzy name
suggestions. The candidate count is capped before metadata is fetched.

It fetches dates and downloads concurrently, removes unavailable metadata,
applies an optional date filter, sorts the inspected results and applies the
display limit. Download counts that are unavailable are shown as missing and,
according to the script's message, sorted last.

The selected candidates are ranked by name relevance. Increasing the number
of inspected candidates may therefore affect which packages reach the final
ranking; the table is not a guaranteed global ranking of every matching project.

<!-- pman:section options views=long,detailed -->
## Options confirmed by the excerpt

| Option | Effect |
| --- | --- |
| `--candidates N` | Maximum name matches to inspect; default 80, maximum 500 |
| `--threads N` | Concurrent metadata fetches; default 4, maximum 16 |
| `--with-conda` | Show exact normalized-name matches from conda-forge |
| `--csv FILE` | Save the final result rows as CSV |
| `--pdf FILE` | Save a multipage results PDF; requires ReportLab |
| `--install` | Prompt for displayed package numbers to install with pip |

`--threads` uses a positive-number parser. The implementation
also uses `--match`, `--sort`, `--period`, `--since`, `--date-field` and `--limit`.
Their complete definitions were outside the supplied excerpt. Consult native
`--help` for choices, date syntax and defaults; this page does not invent them.

`--match any` is explicitly suggested by the script when nothing matches.
`--limit` controls how many sorted, filtered result rows are retained.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Search using multiple keywords:

```bash
search-python-packages neuroscience statistics
```

Try the script's suggested broader matching mode:

```bash
search-python-packages --match any neuroscience behaviour
```

Inspect more candidates while using four metadata workers:

```bash
search-python-packages markdown --candidates 120 --threads 4
```

Show matching conda-forge names and export the results:

```bash
search-python-packages markdown --with-conda --csv markdown-packages.csv
search-python-packages markdown --pdf markdown-results.pdf
```

Choose packages interactively after inspecting the table:

```bash
search-python-packages markdown --install
```

The prompt accepts selections such as `1, 3-5`. pip is invoked through the
Python interpreter running the original script. Choose that script's Python
environment deliberately; the wrapper does not choose a different interpreter.

Read personal help, or export that help for study:

```bash
search-python-packages --long-help --paging never
search-python-packages --list-examples
search-python-packages --all-help --save-only packages-help.html
search-python-packages --all-help --save-only packages-help.pdf
```

Preview the help in a browser:

```bash
pman search-python-packages --all --save packages-help.html --serve
```

<!-- pman:section exports views=detailed -->
## Results exports versus help exports

The original command's `--csv` and `--pdf` export the **search results**.
Its results PDF uses ReportLab. The personal viewer's `--save` and `--save-only`
export the **help page**; HTML/PDF help exports use Pandoc, and PDF additionally
needs a LaTeX engine. The leading personal-help flag tells the wrapper which
kind of request is being made.

```bash
# Results from an actual search:
search-python-packages markdown --pdf results.pdf

# Documentation, without searching:
search-python-packages --all-help --save-only help.pdf --save-log help.log
```

<!-- pman:section limits views=detailed -->
## Dates, availability and interpretation

The table labels dates as first and last upload times in UTC. A missing date
fails the optional `--since` filter. Date filtering happens after candidate
selection and metadata fetching; widening the displayed result limit alone
cannot recover projects excluded at the candidate-selection stage.

conda-forge matching is by normalized package name. This is a name comparison,
not a check of package versions, platforms, dependencies or successful solver
installation. Missing download counts do not mean zero downloads.

The missing parts of the script prevent confirming its download provider,
cache behaviour, full date parser and all accepted sort values. Keep these
details synchronized with the complete script when it is available.

<!-- pman:section errors views=detailed -->
## Exit status and dependency failures

The visible main function returns 0 on successful completion and 1 when the
index cannot be loaded, matches or metadata are unavailable, no inspected
project passes filtering, an export fails, or installation is aborted.
Its argparse validation uses the normal argument-error exit status 2.

The wrapper returns the original command's exit status for ordinary requests.
If the original executable is missing, it returns 127. Personal-help requests
return the viewer's status and never proceed to search or install packages.
Additional failures in omitted functions may behave differently.

<!-- pman:section candidate-ranking views=technical -->
## Why the candidate cap matters

Let $M(Q)$ be the set of name matches for query $Q$, and let $C_k(Q)$ contain
at most $k$ candidates chosen by name relevance. Let $F$ retain candidates with
available metadata and any requested date restriction. The displayed set is

$$
R(Q)=\operatorname{first}_{\ell}
\left(\operatorname{sort}_{s}\left(F(C_k(Q))\right)\right),
$$

where $s$ is the chosen sort key and $\ell$ is the display limit. Thus,

$$
R(Q)\subseteq C_k(Q)\subseteq M(Q).
$$

A matching project outside $C_k(Q)$ cannot appear, even if it would rank very
highly by downloads or date. In a date-filtered search, it is possible to get
no displayed rows while uninspected matching projects would satisfy the date
restriction. Fuzzy suggestions follow the same inspection cap.

Download frequency measures recorded download activity. It is not, by itself,
an estimate of scientific validity or suitability for your task.

<!-- pman:section linking views=detailed -->
## Link to this page

Stable ID: `tools.search-python-packages`.
Aliases: `search-python-packages`, `search-py-pkgs`.
Markdown path: `pages/search-python-packages.md`.

The wrapper defaults to delegating ordinary work to
`/usr/local/bin/search-python-packages`, the path in the supplied listing.
To use another original executable, set `SEARCH_PYTHON_PACKAGES_ORIGINAL` to
its absolute path. It must not point back to the wrapper.

Documentation prepared on 2026-10-02 from the supplied partial script listing.
Native `--help` is the authority for options omitted from that listing.
