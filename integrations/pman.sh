# Source this file from Bash or Zsh. Help must be checked before doing any work.
# The ordinary --help stays under the caller's control. --all is opt-in.

# ----- Help requests -----------------------------------------------------------

function pman_is_help_request {
  case "${1-}" in
    --long-help|--detailed|--detailed-help|--technical-help)
      return 0
      ;;
    --all-help|--list-examples)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

function pman_show_help {
  if (( $# < 1 )); then
    printf 'Usage: pman_show_help PAGE_ID [VIEW] [OPTIONS]\n' >&2
    return 2
  fi
  local page_id="$1"
  shift
  "${PMAN_BIN:-pman}" "$page_id" "$@"
}

# ----- Export helper -----------------------------------------------------------

function pman_save_help {
  if (( $# < 2 )); then
    printf 'Usage: pman_save_help PAGE_ID OUTPUT [VIEW] [OPTIONS]\n' >&2
    return 2
  fi
  local page_id="$1"
  local output="$2"
  shift 2
  "${PMAN_BIN:-pman}" "$page_id" --save "$output" "$@"
}
