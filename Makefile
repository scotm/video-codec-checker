SHELL := bash
.DEFAULT_GOAL := help

UV ?= uv
PYTEST ?= $(UV) run python -m pytest tests/
RUFF ?= $(UV) run ruff
MYPY ?= $(UV) run mypy

.PHONY: help check lint format type test release

help:
	@echo "Targets:"
	@echo "  check    Run lint, type-check, and tests"
	@echo "  lint     Run ruff with --fix"
	@echo "  format   Run ruff formatter"
	@echo "  type     Run mypy on package"
	@echo "  test     Run pytest"
	@echo "  release  Create a GitHub Release for VERSION (uses gh)"
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
	@tag=v$(VERSION); \
	if git rev-parse $$tag >/dev/null 2>&1; then \
	  echo "Tag $$tag already exists"; \
	else \
	  git tag -a $$tag -m "$$tag: $${TITLE:-Release}$$([ -n "$(NOTES)" ] && printf "\n\n%s" "$(NOTES)")"; \
	  git push --tags; \
	fi; \
	if gh release view $$tag >/dev/null 2>&1; then \
	  echo "GitHub Release $$tag already exists"; \
	  gh release edit $$tag $$( [ -n "$(TITLE)" ] && echo --title "$(TITLE)" ) $$( [ -n "$(NOTES)" ] && echo --notes "$(NOTES)" || echo --generate-notes ); \
	else \
	  gh release create $$tag $$( [ -n "$(TITLE)" ] && echo --title "$(TITLE)" ) $$( [ -n "$(NOTES)" ] && echo --notes "$(NOTES)" || echo --generate-notes ); \
	fi
