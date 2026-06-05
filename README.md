perma-status
============

A static GitHub Pages site for [status.perma.cc](https://status.perma.cc/).
A daily GitHub Actions workflow regenerates the page; a human-edited
`docs/status.json` controls the "up / down" banner.

## How it works

- **`docs/`** is the source GitHub Pages serves. Configure the repo
  under Settings → Pages as "Deploy from a branch" with source `main`
  / `/docs`.
- **`docs/index.html`** is regenerated daily at 00:16 UTC by
  [`.github/workflows/regenerate.yml`](.github/workflows/regenerate.yml),
  which runs `python index.py` against the Perma daily-link-counts API
  and the Cloudflare GraphQL API and commits the rendered HTML back to
  this branch. The same workflow can be triggered manually from the
  Actions tab (workflow_dispatch).
- **`docs/status.json`** is the source of truth for the banner shown on
  the page. The HTML loads `static/banner.js`, which fetches
  `status.json?t={timestamp}` (cache-buster) on each pageload and fills
  in `<span id="status">` and `<p id="message">`. To flip the banner,
  edit `docs/status.json` directly on github.com and commit; GitHub
  Pages republishes in roughly a minute.
- **`docs/static/`** holds the CSS, fonts, favicon, and `banner.js`.
  These don't need building; they're served as-is.

```jsonc
// docs/status.json
{
  "up": "up!",                  // text after "Perma.cc is "
  "message": ""                 // optional <p> under the heading
}
```

For planned maintenance:

```json
{
  "up": "in maintenance",
  "message": "Perma.cc is undergoing scheduled maintenance from 18:00–19:00 ET. Captures may be delayed."
}
```

The page falls back to "up!" with an empty message if the fetch fails
for any reason, so a malformed `status.json` won't take the banner
hostage.

## Local development

Dependencies are managed with [uv](https://docs.astral.sh/uv/). The
GitHub Actions workflow uses the same `pyproject.toml` and `uv.lock`,
so what builds locally builds in CI.

```sh
cp .env.example .env       # then fill in API credentials
just build                 # render docs/index.html
just dev                   # serve docs/ at http://localhost:8000
```

`uv run` (under the `build` recipe) resolves dependencies and creates
`.venv/` on first run. The `dev` recipe is `python -m http.server -d docs`
— edit `docs/status.json` and refresh to see the banner change.

To add or upgrade a dependency:

```sh
uv add requests
uv lock --upgrade-package requests
```

Commit the resulting `pyproject.toml` and `uv.lock`.

## Operational notes

- **Secrets** for the workflow live in the repo's GitHub Actions
  secrets: `CF_ZONE`, `CF_API_TOKEN`, `PERMA_DAILY_LINK_COUNTS_ENDPOINT`,
  `PERMA_API_KEY`. The values come from the same Perma + Cloudflare
  accounts as the previous Salt-pillar / Secrets-Manager-backed
  deployments.
- **`docs/CNAME`** sets the custom domain to `status.perma.cc`. Pages
  manages the Let's Encrypt cert. The Cloudflare `status.perma.cc`
  CNAME should point at `harvard-lil.github.io` once we cut over.
- **`docs/.nojekyll`** disables Jekyll processing — Pages serves the
  tree as-is.
- **Schedule reliability:** GitHub Actions cron occasionally skips runs
  during platform load. A missed day means yesterday's HTML keeps
  serving. Anyone can rerun manually from the Actions
  tab.

## History

This is a GitHub Pages rewrite of what used to be a uWSGI-backed
Flask app running on the `status-07` EC2 minion (and briefly on an
ECS Fargate service). After removing the active `/monitor` route,
we no longer need a server-side app.
