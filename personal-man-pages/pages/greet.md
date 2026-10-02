# Greeting script

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`examples/greet.sh` prints a greeting. Its purpose in this repository is to show
how a small Bash script can link to a larger help page without embedding it.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
bash examples/greet.sh [--upper] NAME
```

Ordinary `--help` is implemented by the script itself. Put extended-help flags
first: `--long-help`, `--detailed-help`, `--technical-help`, `--list-examples`,
or `--all`. Use `--all-help` when adapting a command that already uses `--all`.

<!-- pman:section options views=long,detailed -->
## Options

`--upper` converts the name to uppercase. `--` stops option interpretation;
use it before a name beginning with a dash. Quote names containing spaces.

For a help request, additional options belong to the viewer: `--paging never`,
`--pager 'less -R'`, `--glow`, `--save FILE` or `--save-only FILE`.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Print a greeting:

```bash
bash examples/greet.sh Heini
# Hello, Heini.
```

Preserve a multiword name as one argument:

```bash
bash examples/greet.sh --upper 'Ada Lovelace'
# Hello, ADA LOVELACE.
```

Display help without paging:

```bash
bash examples/greet.sh --long-help --paging never
```

Export the whole page without terminal output:

```bash
bash examples/greet.sh --all --save-only greet.html --save-log greet.log
```

Read the same page directly, without running the greeting script:

```bash
pman greet --list-examples
```

<!-- pman:section errors views=detailed -->
## Failure conditions

The script requires exactly one ordinary name argument. Invalid ordinary
arguments return status 2. A failed help request returns a nonzero status and
does not proceed to print a greeting. Extended help works from this checkout
without installing `pman` because the example supplies the viewer path.

<!-- pman:section implementation views=technical -->
## Implementation

The script keeps its stable ID, `demo.greet`, in one help-routing call. The
registry maps that ID to this page; the script does not need its filename.

Only a leading help flag is intercepted. A help-looking string after `--` can
therefore be an ordinary name. The `--all` spelling is explicitly enabled in
this example; the shared adapter does not reserve it for every script.

Uppercase conversion uses Bash's `${name^^}` expansion and the active locale.
It is an example feature, not a Unicode text-normalization tool.
