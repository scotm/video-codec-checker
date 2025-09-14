SHELL := bash
.DEFAULT_GOAL := help

UV ?= uv
PYTEST ?= $(UV) run python -m pytest tests/
RUFF ?= $(UV) run ruff
MYPY ?= $(UV) run mypy

.PHONY: help check lint format type test release release_auto

help:
	@echo "Targets:"
	@echo "  check    Run lint, type-check, and tests"
	@echo "  lint     Run ruff with --fix"
	@echo "  format   Run ruff formatter"
	@echo "  type     Run mypy on package"
	@echo "  test     Run pytest"
	@echo "  release  Create a GitHub Release for VERSION (uses gh); combines curated + auto notes by default"
	@echo "  release_auto  Alias for release (kept for compatibility)"
	@echo ""
	@echo "Examples:"
	@echo "  make check"
	@echo "  make release VERSION=0.5.1 TITLE=\"Bugfixes\" NOTES=\"Details...\""

check: lint type test

lint:
	$(RUFF) check . --fix

format:
	$(RUFF) format .

type:
	$(MYPY) video_codec_checker/

test:
	$(PYTEST)

# Create a GitHub Release from an existing tag.
# Usage: make release VERSION=0.5.1 [TITLE="..."] [NOTES="..."]
release:
	@[ -n "$(VERSION)" ] || (echo "ERROR: VERSION is required (e.g., make release VERSION=0.5.1)" >&2; exit 2)
	@git diff --quiet || (echo "ERROR: Working tree has uncommitted changes" >&2; exit 2)
	@git diff --cached --quiet || (echo "ERROR: Staged changes not committed" >&2; exit 2)
	@which gh >/dev/null 2>&1 || (echo "ERROR: GitHub CLI (gh) not found" >&2; exit 2)
	@gh auth status >/dev/null 2>&1 || (echo "ERROR: gh not authenticated. Run: gh auth login" >&2; exit 2)
	@tag=v$(VERSION); prev=$$(git tag --sort=-version:refname | sed -n '2p'); repo=$$(gh repo view --json nameWithOwner -q .nameWithOwner); \
	if ! git rev-parse $$tag >/dev/null 2>&1; then \
	  git tag -a $$tag -m "$$tag: $${TITLE:-Release}"; \
	  git push --tags; \
	fi; \
	# Build combined notes: curated (NOTES_FILE or NOTES) + auto-generated
	: > .combined-notes.md; \
	if [ -n "$(NOTES_FILE)" ]; then \
	  cat "$(NOTES_FILE)" >> .combined-notes.md; \
	elif [ -n "$(NOTES)" ]; then \
	  printf "%s\n" "$(NOTES)" >> .combined-notes.md; \
	fi; \
	printf "\n---\n\nAuto-generated notes\n\n" >> .combined-notes.md; \
	gh api repos/$$repo/releases/generate-notes -f tag_name="$$tag" -f previous_tag_name="$$prev" --jq .body > .auto-notes.md; \
	cat .auto-notes.md >> .combined-notes.md; \
	if gh release view $$tag >/dev/null 2>&1; then \
	  gh release edit $$tag $$( [ -n "$(TITLE)" ] && echo --title "$(TITLE)" ) --notes-file .combined-notes.md; \
	else \
	  gh release create $$tag $$( [ -n "$(TITLE)" ] && echo --title "$(TITLE)" ) --notes-file .combined-notes.md; \
	fi; \
	rm -f .combined-notes.md .auto-notes.md

# Create a GitHub Release and append auto-generated notes to curated notes.
# Usage: make release_auto VERSION=0.7.0 [TITLE="..."] [NOTES_FILE=release-notes-v0.7.0.md]
release_auto: release
