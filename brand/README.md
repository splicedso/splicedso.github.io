# Spliced brand kit

The mark (27 October 2026) is an upright bar with pointed ends: 250 wide, 750 tall, points 85 deep,
corners rounded at 26. Every file here comes from `build.py` (marks, lockups, tiles, icons, share
images) and `linkedin.py` (LinkedIn banners and the post poster). Edit those, not the files.

    uv run --with fonttools --with uharfbuzz python brand/build.py
    uv run --with pillow python brand/linkedin.py

## Colours

| Scheme | Mark | Ink | Ground |
|---|---|---|---|
| Black | `#000` | `#000` | `#fff` |
| White | `#fff` | `#fff` | `#000` |
| Meta blue | `#0082FB` to `#0064E0` | `#1C2B33` | `#fff`, or `#0064E0` reversed |

The wordmark is Helvetica Neue Medium, stored as outlines.

## Files

| Use | Black | White | Meta blue |
|---|---|---|---|
| Mark alone | `mark-black` | `mark-white` | `mark-meta` |
| Mark and name | `lockup-black` | `lockup-white` | `lockup-meta`, `lockup-meta-reverse` |
| Profile picture | `tile-black-on-white` | `tile-white-on-black` | `tile-meta-on-white`, `tile-white-on-meta` |
| App icon | `icon-black-on-white` | `icon-white-on-black` | `icon-white-on-meta` |
| Share image | `og-white` | `og-black` (the site's) | `og-meta` |
| LinkedIn banner | `linkedin-banner-white` | `linkedin-banner-black` | `linkedin-banner-meta` |
| LinkedIn post (4:5) | `linkedin-poster-white` | | |

Each comes as `.svg` and `.png`. Foundry's app icon (`foundry-icon`) is the white-on-black icon.
