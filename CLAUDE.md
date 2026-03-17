# huje-tools.web.landingpage.src

Public landing page for [huje.tools](https://huje.tools). Static HTML hosted on GitHub Pages.

## Structure

```
docs/                    ← GitHub Pages source (served from main branch)
  index.html             ← Main landing page — 5 tool cards with code examples
  social-alignment.html  ← /social-alignment docs page
  nostr-profile.html     ← /nostr-profile docs page
  sense-memory.html      ← /sense-memory docs page
  sense-music.html       ← /sense-music docs page
  socialcard.html        ← /socialcard docs page
  support.html           ← /support — terms and contact
  og-image.png           ← Main site OG image
  og-sense-memory.png    ← Per-tool OG images (generated with socialcard)
  og-nostr-profile.png
  og-social-alignment.png
  og-sense-music.png
  og-socialcard.png
  CNAME                  ← Custom domain: huje.tools
```

## How to Work With This Repo

- **No build step.** Edit HTML directly. Push to `main` and GitHub Pages deploys.
- **No JavaScript** (except Plausible analytics). Pure HTML + inline CSS.
- **Design system:** Dark theme. `--bg: #0f172a`, `--card: #1e293b`, `--orange: #f97316`, `--text: #f8fafc`. System font stack, monospace for code.
- **Code highlighting:** `.kw` (purple), `.str` (green), `.fn` (blue), `.comment` (dim gray).
- **Mobile responsive.** Media query at 600px.
- **Reduced motion.** `prefers-reduced-motion` disables transitions.
- **Plausible analytics** on every page — same snippet in every `<head>`.

## Tool Pages Pattern

Each tool gets a dedicated page following the same template:
1. Breadcrumb (`huje.tools / toolname`)
2. Hero with tagline, install bar, links (PyPI, ClawHub, Source, Docs)
3. Quickstart code block
4. How it works / capabilities
5. API reference with tables
6. Security section
7. Configuration tables
8. NIPs used (if applicable)
9. Ecosystem section (links to NSE and sibling tools)
10. Footer

OG images generated with `socialcard` package (eating our own dogfood).

## Conventions

- Inline CSS only (no external stylesheets)
- Tool cards on index link to PyPI (primary), ClawHub, Source, and Docs (per-tool page)
- Example code uses generic names: `Johnny5`, `johnny5@example.com`, `https://example.com`
- Brand references only in footers and company attribution (humanjava.com)
- `relay.nostrkeep.com` is the default relay in examples (our product)
- Keep claims honest — only show what's live and working
