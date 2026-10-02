#!/usr/bin/env bash
# Install a symlink to the checkout; do not copy or freeze the help pages.
set -euo pipefail

function show_help {
  cat <<'HELP'
Usage: bash scripts/install.sh [--bin-dir DIRECTORY] [--uninstall]

Install pman into ~/.local/bin by default. No sudo, pip or Python packages.
The repository must remain in place because installation uses a symlink.
Existing files and symlinks owned by other installations are never replaced.

Examples:
  bash scripts/install.sh
  bash scripts/install.sh --bin-dir "$HOME/bin"
  bash scripts/install.sh --uninstall
HELP
}

# ----- Arguments ---------------------------------------------------------------

bin_directory="$HOME/.local/bin"
uninstall=false
while (( $# )); do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    --bin-dir)
      if (( $# < 2 )) || [[ -z "$2" ]]; then
        printf '%s\n' '--bin-dir requires a directory.' >&2
        exit 2
      fi
      bin_directory="$2"
      shift 2
      ;;
    --uninstall)
      uninstall=true
      shift
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

# ----- Install or remove only our own link -------------------------------------

repository_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
launcher="$repository_root/bin/pman"
destination="$bin_directory/pman"

if [[ -e "$destination" || -L "$destination" ]]; then
  if [[ ! -L "$destination" ]] ||
    [[ "$(readlink -- "$destination")" != "$launcher" ]]; then
    printf 'Refusing to modify an unrelated path: %s\n' "$destination" >&2
    exit 2
  fi
  if $uninstall; then
    rm -- "$destination"
    printf 'Removed %s\n' "$destination"
  else
    printf 'Already installed: %s\n' "$destination"
  fi
  exit 0
fi
if $uninstall; then
  printf 'No installation at %s\n' "$destination"
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3.10 or newer is required. See README.md.\n' >&2
  exit 2
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 2)' || {
  printf 'Python 3.10 or newer is required.\n' >&2
  exit 2
}
mkdir -p -- "$bin_directory"
chmod +x -- "$launcher"
ln -s -- "$launcher" "$destination"
printf 'Installed %s\nAdd that directory to PATH if needed.\n' "$destination"
