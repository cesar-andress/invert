# Resolve repository root from any script location.
# Usage: source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"
if [[ -z "${INVERT_REPO_ROOT:-}" ]]; then
  _lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  INVERT_REPO_ROOT="$(cd "${_lib_dir}/../.." && pwd)"
  export INVERT_REPO_ROOT
fi
cd "${INVERT_REPO_ROOT}"
