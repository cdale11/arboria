#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
host="${ARBORIA_HOST:-0.0.0.0}"
port="${ARBORIA_PORT:-8765}"

if [[ "$host" == *$'\n'* || "$port" == *$'\n'* ]]; then
  printf '%s\n' "ARBORIA_HOST and ARBORIA_PORT must be single-line values." >&2
  exit 2
fi

if [[ ! "$port" =~ ^[0-9]+$ ]] || (( port < 1 || port > 65535 )); then
  printf 'Invalid ARBORIA_PORT: %s\n' "$port" >&2
  exit 2
fi

if [[ -n "${CONDA_EXE:-}" && -f "$(dirname -- "$CONDA_EXE")/../etc/profile.d/conda.sh" ]]; then
  conda_sh="$(dirname -- "$CONDA_EXE")/../etc/profile.d/conda.sh"
elif [[ -f "/home/umang/miniconda3/etc/profile.d/conda.sh" ]]; then
  conda_sh="/home/umang/miniconda3/etc/profile.d/conda.sh"
elif command -v conda >/dev/null 2>&1; then
  conda_base="$(conda info --base)"
  conda_sh="$conda_base/etc/profile.d/conda.sh"
else
  printf '%s\n' "Conda was not found. Install Miniconda/Conda and create the arboria environment first." >&2
  exit 1
fi

if [[ ! -f "$conda_sh" ]]; then
  printf 'Conda activation script not found: %s\n' "$conda_sh" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$conda_sh"
conda activate arboria

export PATH="$CONDA_PREFIX/bin:$PATH"
export ARBORIA_REPO_ROOT="$script_dir"
export ARBORIA_STATIC_DIR="$script_dir/web/dist"
export ARBORIA_HOST="$host"
export ARBORIA_PORT="$port"
export PYTHONPATH="$script_dir/src${PYTHONPATH:+:$PYTHONPATH}"
export ARBORIA_DATA_DIR="${ARBORIA_DATA_DIR:-$script_dir/var}"

printf 'Arboria using Conda environment: %s\n' "$CONDA_PREFIX"
printf 'Node: %s (%s)\n' "$(node --version)" "$(command -v node)"
printf 'npm: %s (%s)\n' "$(npm --version)" "$(command -v npm)"
python -m arboria.app.auth_setup

if [[ ! -d "$script_dir/web/node_modules" ]]; then
  printf '%s\n' "Installing locked browser dependencies with npm ci..."
  npm --prefix "$script_dir/web" ci
fi

build_stamp="$script_dir/web/dist/.arboria-build-stamp"
current_fingerprint="$(
  cd "$script_dir"
  python - <<'PY'
from hashlib import sha256
from pathlib import Path

paths = [Path("web/package-lock.json"), Path("web/package.json"), Path("web/tsconfig.json")]
paths.extend(sorted(Path("web/src").rglob("*")))
paths.append(Path("web/index.html"))
digest = sha256()
for path in paths:
    if path.is_file():
        digest.update(str(path).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
print(digest.hexdigest())
PY
)"

previous_fingerprint=""
if [[ -f "$build_stamp" ]]; then
  previous_fingerprint="$(<"$build_stamp")"
fi

if [[ "$current_fingerprint" != "$previous_fingerprint" ]]; then
  printf '%s\n' "Building browser assets..."
  npm --prefix "$script_dir/web" run build
  printf '%s\n' "$current_fingerprint" > "$build_stamp"
fi

printf 'Serving Arboria baseline at http://localhost:%s\n' "$port"
printf 'LAN clients should use this machine address with port %s. Do not browse to 0.0.0.0.\n' "$port"
exec python -m uvicorn arboria.app.server:app --host "$host" --port "$port"
