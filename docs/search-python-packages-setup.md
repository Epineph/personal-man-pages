# Add the search-python-packages personal page

This add-on supplies a tagged Markdown page, its registry entry, a Bash wrapper
and a registration script. It assumes the original command is installed at
`/usr/local/bin/search-python-packages`, as in the supplied terminal listing.

## Extract into the existing checkout

Assuming the downloaded archive is in `~/Downloads`:

```bash
cd "$HOME/my_repos/personal-man-pages"
unzip "$HOME/Downloads/search-python-packages-help-addon.zip" -d .
python3 scripts/register-search-python-packages.py --install-wrapper
python3 bin/pman --check
```

The registration script merges one entry into `registry.json` and preserves
unrelated pages. Re-running it with the same entry is harmless. If its stable
ID or aliases conflict with an existing, different entry, it stops for manual
merging. It refuses to replace an unrelated file in the wrapper directory.

## Activate the wrapper in this shell

```bash
export PATH="$HOME/.local/bin:$PATH"
rehash  # Zsh; use 'hash -r' in Bash
command -v search-python-packages
```

The final command should print a path under `~/.local/bin`. The wrapper link
points into this checkout, so keep the checkout in place. Add the PATH line to
`.zshrc` once if needed. An existing shell alias or function of the same name
can take precedence; `type -a search-python-packages` reveals that situation.

## Read, search and save

```bash
search-python-packages --long-help
search-python-packages --list-examples --paging never
search-python-packages --technical-help
search-python-packages --all-help --save-only packages-help.html
search-python-packages markdown --with-conda --csv markdown-packages.csv
```

You can read the page without installing the wrapper or the original tool:

```bash
python3 bin/pman search-python-packages --all --paging never
```

You can also use the wrapper directly before installing its symlink:

```bash
bash wrappers/search-python-packages --long-help --paging never
```

Native `--help` comes from the original executable, with the personal-help
choices appended. Ordinary search arguments and exit statuses pass through.
The wrapper uses `--all-help`; `--all` is not intercepted. The attachment did
not include the complete parser, so the page explicitly leaves unconfirmed
choices to native `--help` rather than inventing them.

## Use another original executable

```bash
export SEARCH_PYTHON_PACKAGES_ORIGINAL="/absolute/path/to/original-script"
```

Set this only to an executable script or binary, not to the wrapper link.
When using a virtual environment, the original executable's shebang still
determines its interpreter. The wrapper passes arguments without rewriting them.

## Remove the command wrapper

If `~/.local/bin/search-python-packages` is still the link created above:

```bash
ls -l "$HOME/.local/bin/search-python-packages"
rm "$HOME/.local/bin/search-python-packages"
rehash
```

This removes only the user-level link. The personal page remains readable
through `pman`, and the installed original command remains available at its
original path. Use `hash -r` instead of `rehash` in Bash.
