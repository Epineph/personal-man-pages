# Source integrations/pman.sh first, then this file, from Bash or Zsh.

function croot {
  if pman_is_help_request "$@" || [[ "${1-}" == --all ]]; then
    pman_show_help demo.croot "$@"
    return $?
  fi
  case "${1-}" in
    -h|--help)
      printf 'Usage: croot\nChange to $PMAN_HOME in the current shell.\n'
      printf 'More: --long-help, --list-examples, --all\n'
      return 0
      ;;
  esac
  if (( $# != 0 )); then
    printf 'croot accepts no ordinary arguments. Use --help.\n' >&2
    return 2
  fi
  if [[ -z "${PMAN_HOME-}" ]]; then
    printf 'Set PMAN_HOME to your personal-man-pages checkout first.\n' >&2
    return 2
  fi
  builtin cd -- "$PMAN_HOME"
}
