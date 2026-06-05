# `just` recipes for local development.
#
# Run `just` with no arguments to list available recipes.

default:
    @just --list

# Render docs/index.html from the live Perma + Cloudflare APIs (reads .env).
build:
    mkdir -p docs
    uv run python index.py > docs/index.html.new
    mv docs/index.html.new docs/index.html

# Serve docs/ on http://localhost:8000 — preview as GitHub Pages will serve it.
dev:
    uv run python -m http.server -d docs
