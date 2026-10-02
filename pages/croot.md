# Change to the help repository

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`croot` changes the current shell's working directory to `$PMAN_HOME`.
It demonstrates extended help for a shell function, rather than an executable.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
croot
croot --long-help
croot --list-examples
croot --all
```

Load the shared adapter and function definition into Bash or Zsh first.
Set `PMAN_HOME` to the repository directory and make `pman` available on `PATH`.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Load the example for this shell session:

```bash
export PMAN_HOME="$HOME/repos/personal-man-pages"
source "$PMAN_HOME/integrations/pman.sh"
source "$PMAN_HOME/examples/croot.sh"
croot
```

Display help without changing the working directory:

```bash
croot --long-help --paging never
```

Call the export function directly:

```bash
pman_save_help demo.croot "$HOME/croot.html" --all-help
```

<!-- pman:section errors views=detailed -->
## Failure conditions

An unset or empty `PMAN_HOME`, unsupported arguments, or a failed directory
change produces a nonzero status. A requested help view returns the viewer's
status. The function does not continue to change directories after showing help.
