# splicedso.github.io

The Spliced site: a static, multi-page site with no framework.

```bash
uv run --with markdown python build.py
```

`build.py` renders `src/pages/*` into `src/base.html`, turns each research note in the sibling `phase/notes` checkout into a page (a `<!-- chart:NAME -->` line becomes that interactive figure), and writes `assets/data.json` from `phase/results`, so the charts cannot drift from the measurements. Commit the built output; GitHub Pages serves the repository as is.

- `src/`: page sources, `style.css` (light and dark themes from one set of tokens), `site.js` (theme toggle, the gutter bus), `home.js` (token replay, live schematic), `charts.js` (research figures).
- `brand/`: the mark in every variant and scheme (black, white, Meta blue), generated from one geometry. See `brand/README.md`.
- `render/`: Blender scenes for the brand films (not used on the current pages).

To move to a custom domain, set `"domain"` in `site.json` (for example `"spliced.ai"`) and rebuild: the build writes `CNAME` and switches every canonical URL, the sitemap and the link previews. Then point the domain's DNS at GitHub Pages.

CI (`.github/workflows/check.yml`) checks out Phase beside the site, rebuilds, fails if the committed pages differ from a fresh build, and checks every internal link (`check_links.py`).

Preview with `python3 -m http.server`.
