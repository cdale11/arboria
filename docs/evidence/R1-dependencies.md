# R1 dependency baseline evidence

Date: 2026-09-12. Scope: dependency resolution and smoke verification only. This is not evidence that the game, server, launcher, biological simulation, persistence, or application test suite exists.

## Host and environment

- OS/platform: Linux x86-64.
- Conda: 26.3.2, solver `libmamba`, default channels `pkgs/main` and `pkgs/r`.
- Environment: existing `arboria` at `/home/umang/miniconda3/envs/arboria`.
- Python selected: 3.13.15. Python 3.14.7 was replaced because compatibility with the intended numerical stack was unverified and Conda resolved the full stack on Python 3.13.
- Node selected: Conda `nodejs` 26.5.1 with npm 11.17.0.

## Installed direct Conda requirements

The following were resolved and installed through Conda defaults using activated `arboria`: `python=3.13`, `numpy`, `numba`, `fastapi`, `uvicorn`, `pytest`, `hypothesis`, `mypy`, `ruff`, and `nodejs`.

Generated lock: `conda-linux-64.lock` from `conda list --explicit`.

## Installed direct npm requirements

The frontend lock was generated with Conda's Node first in `PATH`:

```bash
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web install --package-lock-only
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web ci
```

Direct browser dependencies: `vite`, `three`, `@vitejs/plugin-basic-ssl`. Direct development dependencies: `typescript`, `vitest`, `jsdom`, `@types/node`, and `@types/three`.

Generated lock: `web/package-lock.json`.

## Commands run

```bash
conda install --dry-run -y python=3.13 numpy numba fastapi uvicorn pytest hypothesis mypy ruff nodejs
conda install -y python=3.13 numpy numba fastapi uvicorn pytest hypothesis mypy ruff nodejs
conda list --explicit > conda-linux-64.lock
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web install --package-lock-only
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web ci
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run check
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run build
python dependency import and Numba JIT smoke check
ruff check .
```

## Results

- Conda dry run resolved the direct stack without pip or system packages.
- Conda install completed successfully.
- TypeScript check passed.
- Vitest/jsdom smoke suite passed: 1 file, 1 test.
- Vite production build passed.
- Python smoke imported NumPy 2.4.6, Numba 0.66.0, FastAPI 0.138.0, Uvicorn 0.52.4, pytest 9.0.3, and Hypothesis 6.165.10.
- Numba compiled and ran a trivial `njit` function.
- Ruff passed for current repository files.

## Limitations

- Browser e2e tooling is not selected or locked yet. `npm --prefix web run test:e2e` intentionally fails until a real e2e suite is implemented.
- The later R1 launcher/server baseline added a minimal FastAPI server and `./run.sh`; this dependency evidence does not cover it.
- No biology, persistence, economy, companion, or gameplay tests exist yet.
- npm warned that `esbuild` has an install script not covered by npm's `allowScripts` review flow. The current Vite build still passed; R1 launcher/setup work must decide whether to explicitly approve or configure allowed package scripts.
- An initial npm lock command accidentally used NVM Node because it appeared earlier in `PATH`; see `MISTAKES.md` M-003. The lock was regenerated with Conda Node first in `PATH`.
