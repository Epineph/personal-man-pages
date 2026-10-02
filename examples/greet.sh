#!/usr/bin/env bash
# A small, complete example of help routing before argument parsing or work.
set -euo pipefail

example_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
source "$example_root/integrations/pman.sh"
PMAN_BIN="${PMAN_BIN:-$example_root/bin/pman}"

# ----- Help --------------------------------------------------------------------

if pman_is_help_request "$@" || [[ "${1-}" == --all ]]; then
  pman_show_help demo.greet "$@"
  exit 0
fi

case "${1-}" in
  -h|--help)
    cat <<'HELP'
Usage: greet.sh [--upper] NAME
Print a greeting, optionally in uppercase.

Extended help (place the flag first):
  --long-help       Practical guide
  --detailed-help   All practical details
  --technical-help Implementation notes
  --list-examples   Usage examples only
  --all            Entire page (--all-help also works)

Help display: --paging never, --pager 'less -R', --glow
Save a view: greet.sh --all --save greet.html
HELP
    exit 0
    ;;
esac

# ----- Ordinary arguments and work --------------------------------------------

uppercase=false
if [[ "${1-}" == --upper ]]; then
  uppercase=true
  shift
fi
if [[ "${1-}" == -- ]]; then
  shift
fi
if (( $# != 1 )); then
  printf 'Expected one name. Use --help.\n' >&2
  exit 2
fi
name="$1"
if $uppercase; then
  name="${name^^}"
fi
printf 'Hello, %s.\n' "$name"
