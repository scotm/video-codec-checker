# Contributing Guide

Thank you for contributing! This repo follows a lightweight Git Flow and keeps a tight feedback loop with linting, formatting, typing, and tests. This document outlines the branching model, day‑to‑day workflow, and the pull request checklist.

## Branching Model (Git Flow)

Long‑lived branches:

- `main` — production release history; tags and GitHub Releases come from here.
- `develop` — integration branch for the next release.

Supporting branches:

- `feature/<topic>` — branch from `develop`; merge back into `develop`.
- `release/<X.Y.Z>` — branch from `develop` to prepare a release; merge into `main` and back into `develop`; tag on `main`.
- `hotfix/<X.Y.Z>` — branch from `main` for urgent fixes; merge into `main` and `develop`; tag on `main`.

Naming suggestions:

- Features: `feature/bpp-consolidation`, `feature/h264-thresholds`, `feature/docs-contributing`
- Releases: `release/0.7.5`
- Hotfixes: `hotfix/0.7.4.1`

## Getting Started

Prereqs: Python ≥ 3.10, `uv` (recommended), GitHub CLI `gh` for releases.

```bash
# Create and activate a virtual environment (uv recommended)
uv venv
source .venv/bin/activate

# Install with dev tools and stubs
uv pip install -e .[dev]

# Optional: install pre-commit hooks (blocks committing generated CSVs)
uv run pre-commit install
```

Useful commands:

- Lint: `uv run ruff check .` (auto-fix: `--fix`)
- Format: `uv run ruff format .`
- Type check: `uv run mypy video_codec_checker/`
- Tests: `uv run python -m pytest tests/` (or `make check` for all)

## Development Workflow

Feature work:

```bash
git checkout develop
git pull --ff-only
git checkout -b feature/<topic>

# Implement changes
uv run ruff format .
uv run ruff check .
uv run mypy video_codec_checker/
uv run python -m pytest tests/

# Commit small, focused changes
git add -p
git commit -m "feat(scope): concise description"
git push -u origin feature/<topic>
```

Open a PR targeting `develop` (unless it is a hotfix). Ensure CI is green.

Release flow (example: `0.7.5`):

```bash
git checkout -b release/0.7.5 develop

# Bump version & docs
# - Update version in pyproject.toml
# - Update README "What's New" (last two releases only)
# - Update CHANGELOG.md (newest first)

make check

# Merge release PR into main
# Tag and publish GitHub Release
make release VERSION=0.7.5 TITLE="v0.7.5: …" [NOTES|NOTES_FILE]

# Merge release branch back into develop
```

Hotfix flow (example: `0.7.4.1`):

```bash
git checkout -b hotfix/0.7.4.1 main

# Fix + bump patch version
make check

# Merge into main, release/tag, then merge back into develop
make release VERSION=0.7.4.1 TITLE="v0.7.4.1: hotfix"
```

## Pull Request Checklist

- [ ] Base branch is `develop` (or `main` for hotfixes only).
- [ ] Code formatted: `uv run ruff format .`.
- [ ] Lint clean: `uv run ruff check .` (use `--fix` when safe).
- [ ] Types clean: `uv run mypy video_codec_checker/`.
- [ ] Tests pass: `uv run python -m pytest tests/`.
- [ ] No changes to CSV/schema unless intentionally appended at the end; tests updated.
- [ ] Docs updated if behavior/CLI/CSV changed.
- [ ] No generated CSVs or temporary notes committed (pre-commit helps enforce).
- [ ] Sensible commit messages; small, focused commits.
- [ ] Appropriate labels applied (e.g., `documentation`, `enhancement`, `bug`, `ci`, `test`, `chore`).

## Code Quality & Style

- Keep `mypy` clean; add precise type hints to new/changed functions. Avoid `typing.Any` unless unavoidable; if used, document why.
- Prefer dataclasses and small typed models over tuples (see `video_codec_checker/models.py`).
- Handle exceptions with clear messages; add tests for error paths where practical.
- Follow existing style and keep changes minimal and focused.

## Testing Guidance

- Do not invoke real `ffprobe`/`ffmpeg` in unit tests.
- Patch `subprocess.run` and `shutil.which` in tests for determinism.
- Control discovery by patching helpers (e.g., `get_video_files`) to avoid real filesystem scans.
- Prefer `jobs=1` in tests or inject a serial probe function for ordering stability.
- When script/CSV content is asserted, write into a `TemporaryDirectory` and assert on files.

## Releases & Notes

- Use `make release` to create a tag `vX.Y.Z` and publish a GitHub Release. The Makefile combines curated notes (`NOTES` or `NOTES_FILE`) with auto-generated notes by default.
- Keep README “What’s New” to the last two releases; older entries move to `CHANGELOG.md` (descending version order).

## CI Expectations

CI runs Python {3.10, 3.11, 3.12} and requires:

- `ruff format --check .` and `ruff check .` to pass.
- `mypy video_codec_checker/` to pass (install missing `types-` stubs in `[project.optional-dependencies].dev`).
- `pytest` to pass.

## Commit Guidelines

- Break down changes into small, focused commits.
- Stage only relevant hunks (`git add -p`).
- Use clear, descriptive messages (e.g., `feat(ffprobe): fold BPP into primary probe`).
- Ensure each commit is correct and complete (build/tests pass locally).

