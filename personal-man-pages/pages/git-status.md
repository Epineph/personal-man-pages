# Personal git status guide

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`git status` shows differences between the index and the current commit,
differences between the working tree and the index, and untracked paths.
This page focuses on the checks useful before staging or committing files.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
git status
git status --short --branch
```

Read this personal guide with `pman git-status`. The native Git command keeps
its own flags and help. No alias replaces it.

<!-- pman:section interpretation views=long,detailed -->
## Reading short output

In ordinary short output, the first status column describes the index relative
to `HEAD`; the second describes the working tree relative to the index.
`??` indicates an untracked path. Unmerged paths use conflict-specific codes.

For example, `M ` is a staged modification and ` M` is an unstaged modification.
`MM` means the file was staged and then modified again in the working tree.
Inspect the two changes with `git diff --cached` and `git diff`, respectively.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Get a compact view with branch information:

```bash
git status --short --branch
```

List individual untracked files inside directories:

```bash
git status --short --untracked-files=all
```

Limit the inspection to documentation and integrations:

```bash
git status --short -- pages integrations
```

Use a stable, machine-readable status format in another script:

```bash
git status --porcelain=v1 -z
```

`-z` uses NUL-separated records. A script must parse the documented record
format, including the special handling of renames; ordinary line splitting is
not sufficient. This command is an illustration, not a parser implementation.

<!-- pman:section cautions views=detailed -->
## Important distinctions

An untracked file is not ignored by definition: ignore rules may suppress it.
Use `git status --ignored` when investigating ignored files. The displayed
branch relationship describes locally available tracking information; this
command does not fetch updates from a remote.

<!-- pman:section provenance views=long,detailed -->
## Source and review

This is an original, selective summary of the
[official git-status documentation](https://git-scm.com/docs/git-status),
reviewed on 2026-10-02. Check `git --version` and the matching documentation
when behavior differs. The native manual remains the complete reference.
